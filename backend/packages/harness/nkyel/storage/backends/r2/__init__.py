"""Cloudflare R2 / S3-compatible content-addressed blob store backend."""
from .r2_store import R2BlobStore

STORE_CLASS = R2BlobStore

__all__ = ["R2BlobStore", "STORE_CLASS"]
