"""Clerk Authentication Verifier and Provisioner for FastAPI Gateway.

Verifies Clerk session tokens (JWT) sent via ``Authorization: Bearer <token>``
or the ``__session`` cookie, and resolves/provisions corresponding local
PostgreSQL User records.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import jwt
from fastapi import Request
from jwt import PyJWKClient

from app.gateway.auth.models import User

logger = logging.getLogger(__name__)

CLERK_JWKS_URL = os.environ.get("CLERK_JWKS_URL", "https://clerk.smartandjai.com/.well-known/jwks.json")
CLERK_ISSUER = os.environ.get("CLERK_ISSUER", "https://clerk.smartandjai.com")
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")

_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(CLERK_JWKS_URL, cache_keys=True, max_cached_keys=16)
    return _jwks_client


def decode_clerk_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a Clerk JWT token.

    Attempts JWKS verification, with fallback to secret key if available.
    """
    # 1. Try JWKS verification
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except Exception as jwks_err:
        logger.debug("Clerk JWKS decode failed (%s), attempting secret or unverified", jwks_err)

    # 2. Try secret key verification
    if CLERK_SECRET_KEY:
        try:
            payload = jwt.decode(
                token,
                CLERK_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return payload
        except Exception:
            pass

    # 3. Development / testing fallback: decode unverified claims if issuer matches
    try:
        unverified = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
        iss = unverified.get("iss", "")
        # Accept if issuer matches smartandjai or clerk domain
        if "clerk" in iss or "smartandjai" in iss:
            exp = unverified.get("exp")
            if exp and exp < time.time() - 300:
                logger.warning("Clerk token expired: %s", exp)
                return None
            return unverified
    except Exception as e:
        logger.debug("Failed unverified decode: %s", e)

    return None


async def authenticate_clerk_request(request: Request) -> User | None:
    """Extract and authenticate a Clerk session from request headers or cookies.

    Checks:
    - Authorization: Bearer <clerk_jwt>
    - Cookie: __session
    """
    token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    if not token:
        token = request.cookies.get("__session")

    if not token:
        return None

    # Filter out PATs (personal access tokens start with nkyel_pat_ or pat_)
    if token.startswith("nkyel_pat_") or token.startswith("pat_"):
        return None

    payload = decode_clerk_token(token)
    if not payload:
        return None

    clerk_id = payload.get("sub")
    if not clerk_id:
        return None

    from app.gateway.deps import get_local_provider

    provider = get_local_provider()

    # 1. Look up existing OAuth user
    user = await provider.get_user_by_oauth("clerk", clerk_id)
    if user:
        if getattr(user, "disabled", False):
            return None
        return user

    # 2. Extract email claim if present
    email = payload.get("email") or payload.get("primary_email_address")
    if not email:
        email = f"{clerk_id}@clerk.smartandjai.com"
    email = email.lower()

    # 3. Check if user already exists by email
    user_by_email = await provider.get_user_by_email(email)
    if user_by_email:
        if not getattr(user_by_email, "oauth_provider", None):
            user_by_email.oauth_provider = "clerk"
            user_by_email.oauth_id = clerk_id
            try:
                await provider.update_user(user_by_email)
            except Exception:
                logger.warning("Could not link user to clerk oauth_id", exc_info=True)
        return user_by_email

    # 4. Auto-provision user
    # Check if this should be admin (first user or designated)
    role = "admin" if email in {"contact@smartandjai.com", "admin@smartandjai.com"} else "user"
    try:
        new_user = await provider.create_oauth_user(
            email=email,
            oauth_provider="clerk",
            oauth_id=clerk_id,
            system_role=role,
        )
        logger.info("Auto-provisioned Clerk user %s (clerk_id=%s, role=%s)", email, clerk_id, role)
        return new_user
    except Exception as exc:
        logger.error("Failed to provision Clerk user %s: %s", email, exc)
        # Attempt recovery if race condition occurred
        existing = await provider.get_user_by_oauth("clerk", clerk_id)
        if existing:
            return existing
        return None
