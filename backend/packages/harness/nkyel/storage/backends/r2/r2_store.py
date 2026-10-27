"""Cloudflare R2 (S3-compatible) content-addressed blob store backend.

Layout (content-addressed, sharded):
    <prefix>/<kind>/<sha256[:2]>/<sha256>          the bytes
    <prefix>/<kind>/<sha256[:2]>/<sha256>.json     sidecar metadata
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any

from nkyel.storage.contract import (
    BlobNotFoundError,
    BlobReadError,
    BlobRef,
    BlobStore,
    BlobStoreError,
    BlobWriteError,
    validate_blob_kind,
)

logger = logging.getLogger(__name__)

_META_SUFFIX = ".json"
_MAX_BLOB_BYTES = 64 * 1024 * 1024  # 64 MiB defense-in-depth single-put cap


class R2BlobStore(BlobStore):
    """Content-addressed store on Cloudflare R2 / S3-compatible storage."""

    def __init__(
        self,
        *,
        bucket_name: str,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        region_name: str = "auto",
        prefix: str = "blobs",
        public_url: str | None = None,
    ) -> None:
        import boto3
        from botocore.config import Config

        self._bucket_name = bucket_name
        self._endpoint_url = endpoint_url.rstrip("/")
        self._prefix = prefix.strip("/")
        self._public_url = public_url.rstrip("/") if public_url else None

        cfg = Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=30,
        )
        self._client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
            config=cfg,
        )

    @classmethod
    def from_config(cls, backend_config: dict[str, Any]) -> R2BlobStore:
        bucket = backend_config.get("bucket_name") or os.getenv("R2_BUCKET_NAME") or os.getenv("CLOUDFLARE_R2_BUCKET")
        endpoint = backend_config.get("endpoint_url") or os.getenv("R2_ENDPOINT_URL")
        key_id = backend_config.get("access_key_id") or os.getenv("R2_ACCESS_KEY_ID")
        secret = backend_config.get("secret_access_key") or os.getenv("R2_SECRET_ACCESS_KEY")
        region = backend_config.get("region_name") or "auto"
        prefix = backend_config.get("prefix") or "blobs"
        pub = backend_config.get("public_url") or os.getenv("R2_PUBLIC_URL")

        if not bucket or not endpoint or not key_id or not secret:
            raise ValueError(
                "R2BlobStore requires bucket_name, endpoint_url, access_key_id, and secret_access_key (or corresponding env vars)"
            )

        return cls(
            bucket_name=str(bucket),
            endpoint_url=str(endpoint),
            access_key_id=str(key_id),
            secret_access_key=str(secret),
            region_name=str(region),
            prefix=str(prefix),
            public_url=str(pub) if pub else None,
        )

    def _keys_for(self, ref: BlobRef) -> tuple[str, str]:
        p = f"{self._prefix}/" if self._prefix else ""
        base = f"{p}{ref.kind}/{ref.sha256[:2]}/{ref.sha256}"
        return base, f"{base}{_META_SUFFIX}"

    def put_bytes(
        self,
        data: bytes,
        *,
        kind: str,
        content_type: str | None = None,
        thread_id: str | None = None,
    ) -> BlobRef:
        validate_blob_kind(kind)
        if len(data) > _MAX_BLOB_BYTES:
            raise BlobWriteError(f"Refusing to store {len(data)} bytes (cap is {_MAX_BLOB_BYTES})")

        digest = hashlib.sha256(data).hexdigest()
        ref = BlobRef(sha256=digest, size=len(data), kind=kind, content_type=content_type)
        data_key, meta_key = self._keys_for(ref)

        try:
            extra_args: dict[str, Any] = {}
            if content_type:
                extra_args["ContentType"] = content_type

            # Upload main blob
            self._client.put_object(
                Bucket=self._bucket_name,
                Key=data_key,
                Body=data,
                **extra_args,
            )

            # Upload sidecar metadata
            meta = {
                "sha256": ref.sha256,
                "size": ref.size,
                "kind": ref.kind,
                "content_type": content_type,
                "writer_thread_id": thread_id,
                "created_at": time.time(),
            }
            self._client.put_object(
                Bucket=self._bucket_name,
                Key=meta_key,
                Body=json.dumps(meta, ensure_ascii=False).encode("utf-8"),
                ContentType="application/json",
            )
        except Exception as exc:
            raise BlobWriteError(f"Failed to persist blob {ref.sha256[:12]} to R2: {exc}") from exc

        return ref

    def get_bytes(self, ref: BlobRef) -> bytes:
        data_key, _ = self._keys_for(ref)
        try:
            res = self._client.get_object(Bucket=self._bucket_name, Key=data_key)
            data = res["Body"].read()
        except self._client.exceptions.NoSuchKey as exc:
            raise BlobNotFoundError(f"Blob {ref.sha256[:12]} not found in R2 bucket {self._bucket_name}") from exc
        except Exception as exc:
            if "NoSuchKey" in type(exc).__name__ or "404" in str(exc):
                raise BlobNotFoundError(f"Blob {ref.sha256[:12]} not found in R2") from exc
            raise BlobReadError(f"Failed to read blob {ref.sha256[:12]} from R2: {exc}") from exc

        if len(data) != ref.size:
            raise BlobReadError(
                f"Blob {ref.sha256[:12]} size mismatch on read from R2 (got {len(data)}, expected {ref.size})"
            )
        digest = hashlib.sha256(data).hexdigest()
        if digest != ref.sha256:
            raise BlobReadError(
                f"Blob {ref.sha256[:12]} content digest mismatch on read from R2 (got {digest[:12]}, expected {ref.sha256[:12]})"
            )
        return data

    def exists(self, ref: BlobRef) -> bool:
        data_key, _ = self._keys_for(ref)
        try:
            self._client.head_object(Bucket=self._bucket_name, Key=data_key)
            return True
        except Exception:
            return False

    def delete(self, ref: BlobRef) -> None:
        data_key, meta_key = self._keys_for(ref)
        try:
            self._client.delete_objects(
                Bucket=self._bucket_name,
                Delete={"Objects": [{"Key": data_key}, {"Key": meta_key}]},
            )
        except Exception as exc:
            raise BlobStoreError(f"Failed to delete blob {ref.sha256[:12]} from R2: {exc}") from exc

    def close(self) -> None:
        """Release any client resources."""
        pass
