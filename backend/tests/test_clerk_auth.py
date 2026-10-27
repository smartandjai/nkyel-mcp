"""Test Clerk JWT authentication and auto-provisioning."""

import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from app.gateway.auth.clerk import authenticate_clerk_request, decode_clerk_token
from app.gateway.auth.models import User


@pytest.mark.asyncio
async def test_clerk_token_generation_and_decode():
    secret = "a" * 32
    token = jwt.encode(
        {
            "sub": "user_2test_clerk_123",
            "email": "tester@clerk.smartandjai.com",
            "iss": "https://clerk.smartandjai.com",
            "exp": time.time() + 3600,
        },
        secret,
        algorithm="HS256",
    )
    with patch.dict("os.environ", {"CLERK_SECRET_KEY": secret}):
        payload = decode_clerk_token(token)
    assert payload is not None
    assert payload["sub"] == "user_2test_clerk_123"
    assert payload["email"] == "tester@clerk.smartandjai.com"


@pytest.mark.asyncio
async def test_clerk_auth_and_provision():
    secret = "a" * 32
    token = jwt.encode(
        {
            "sub": "user_2test_clerk_456",
            "email": "auto_test@clerk.smartandjai.com",
            "iss": "https://clerk.smartandjai.com",
            "exp": time.time() + 3600,
        },
        secret,
        algorithm="HS256",
    )

    req = MagicMock()
    req.headers = {"authorization": f"Bearer {token}"}
    req.cookies = {}

    mock_provider = MagicMock()
    mock_provider.get_user_by_oauth = AsyncMock(return_value=None)
    mock_provider.get_user_by_email = AsyncMock(return_value=None)
    created_user = User(
        id=str(uuid.uuid4()),
        email="auto_test@clerk.smartandjai.com",
        oauth_provider="clerk",
        oauth_id="user_2test_clerk_456",
        system_role="user",
    )
    mock_provider.create_oauth_user = AsyncMock(return_value=created_user)

    with (
        patch("app.gateway.deps.get_local_provider", return_value=mock_provider),
        patch.dict("os.environ", {"CLERK_SECRET_KEY": secret}),
    ):
        user = await authenticate_clerk_request(req)
        assert user is not None
        assert user.email == "auto_test@clerk.smartandjai.com"
        assert user.oauth_provider == "clerk"
        assert user.oauth_id == "user_2test_clerk_456"
