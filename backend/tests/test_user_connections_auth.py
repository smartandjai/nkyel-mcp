"""Regression tests for User Connections authentication and authorization.

Guarantees that:
1. get_authenticated_user is exported from app.gateway.deps and aliases get_verified_interactive_user.
2. Verified Clerk sessions (AUTH_SOURCE_CLERK) and browser sessions (AUTH_SOURCE_SESSION) are permitted.
3. Anonymous requests are rejected with 401 Unauthorized.
4. Non-interactive identities (PAT, auth-disabled, internal) are strictly forbidden with 403 Forbidden.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, HTTPException, Request
from httpx import ASGITransport, AsyncClient

from app.gateway.auth_disabled import (
    AUTH_SOURCE_AUTH_DISABLED,
    AUTH_SOURCE_CLERK,
    AUTH_SOURCE_INTERNAL,
    AUTH_SOURCE_PAT,
    AUTH_SOURCE_SESSION,
)
from app.gateway.deps import get_authenticated_user, get_verified_interactive_user
from app.gateway.routers import user_connections


def test_dependency_exports():
    """Verify both dependency names are exported and point to the same callable."""
    assert get_authenticated_user is get_verified_interactive_user


@pytest.mark.anyio
async def test_get_verified_interactive_user_direct():
    """Unit test the wrapper logic directly for all auth sources."""
    # 1. Verified Clerk session
    req_clerk = SimpleNamespace(
        state=SimpleNamespace(user=SimpleNamespace(id="clerk_123"), auth_source=AUTH_SOURCE_CLERK),
        cookies={},
    )
    user = await get_verified_interactive_user(req_clerk)  # type: ignore[arg-type]
    assert user.id == "clerk_123"

    # 2. Verified Browser session
    req_session = SimpleNamespace(
        state=SimpleNamespace(user=SimpleNamespace(id="session_456"), auth_source=AUTH_SOURCE_SESSION),
        cookies={},
    )
    user = await get_verified_interactive_user(req_session)  # type: ignore[arg-type]
    assert user.id == "session_456"

    # 3. PAT caller -> 403 Forbidden
    req_pat = SimpleNamespace(
        state=SimpleNamespace(user=SimpleNamespace(id="pat_user"), auth_source=AUTH_SOURCE_PAT),
        cookies={},
    )
    with pytest.raises(HTTPException) as exc_pat:
        await get_verified_interactive_user(req_pat)  # type: ignore[arg-type]
    assert exc_pat.value.status_code == 403
    assert "verified Clerk or browser session" in exc_pat.value.detail

    # 4. Auth-disabled caller -> 403 Forbidden
    req_disabled = SimpleNamespace(
        state=SimpleNamespace(user=SimpleNamespace(id="auth_disabled_user"), auth_source=AUTH_SOURCE_AUTH_DISABLED),
        cookies={},
    )
    with pytest.raises(HTTPException) as exc_disabled:
        await get_verified_interactive_user(req_disabled)  # type: ignore[arg-type]
    assert exc_disabled.value.status_code == 403
    assert "verified Clerk or browser session" in exc_disabled.value.detail

    # 5. Internal system caller -> 403 Forbidden
    req_internal = SimpleNamespace(
        state=SimpleNamespace(user=SimpleNamespace(id="internal_sys"), auth_source=AUTH_SOURCE_INTERNAL),
        cookies={},
    )
    with pytest.raises(HTTPException) as exc_internal:
        await get_verified_interactive_user(req_internal)  # type: ignore[arg-type]
    assert exc_internal.value.status_code == 403
    assert "verified Clerk or browser session" in exc_internal.value.detail

    # 6. Anonymous (no user, no auth source) -> 401 Unauthorized
    req_anon = SimpleNamespace(
        state=SimpleNamespace(user=None, auth_source=None),
        cookies={},
        headers={},
    )
    with pytest.raises(HTTPException) as exc_anon:
        await get_verified_interactive_user(req_anon)  # type: ignore[arg-type]
    assert exc_anon.value.status_code == 401


@pytest.fixture
async def connections_client():
    app = FastAPI()
    app.include_router(user_connections.router)

    identity = SimpleNamespace(id="alice", source=AUTH_SOURCE_SESSION)

    @app.middleware("http")
    async def auth_simulator(request: Request, call_next):
        if identity.id:
            request.state.user = SimpleNamespace(id=identity.id)
            request.state.auth_source = identity.source
        else:
            request.state.user = None
            request.state.auth_source = None
        return await call_next(request)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, identity


@pytest.mark.anyio
async def test_connections_router_unauthenticated_rejected(connections_client):
    """Anonymous requests must return 401 Unauthorized across all endpoints."""
    client, identity = connections_client
    identity.id = None
    identity.source = None

    res_get = await client.get("/api/connections")
    assert res_get.status_code == 401

    res_post = await client.post("/api/connections/authorize", json={"toolkit": "gmail"})
    assert res_post.status_code == 401

    res_delete = await client.delete("/api/connections/gmail")
    assert res_delete.status_code == 401


@pytest.mark.anyio
@pytest.mark.parametrize("disallowed_source", [AUTH_SOURCE_PAT, AUTH_SOURCE_AUTH_DISABLED, AUTH_SOURCE_INTERNAL])
async def test_connections_router_forbidden_sources(connections_client, disallowed_source):
    """PAT, auth-disabled, and internal identities must return 403 Forbidden."""
    client, identity = connections_client
    identity.id = "user_non_interactive"
    identity.source = disallowed_source

    res_get = await client.get("/api/connections")
    assert res_get.status_code == 403
    assert "verified Clerk or browser session" in res_get.text

    res_post = await client.post("/api/connections/authorize", json={"toolkit": "gmail"})
    assert res_post.status_code == 403
    assert "verified Clerk or browser session" in res_post.text

    res_delete = await client.delete("/api/connections/gmail")
    assert res_delete.status_code == 403
    assert "verified Clerk or browser session" in res_delete.text


@pytest.mark.anyio
@pytest.mark.parametrize("allowed_source", [AUTH_SOURCE_SESSION, AUTH_SOURCE_CLERK])
async def test_connections_router_allowed_sources(connections_client, allowed_source):
    """Browser session and Clerk tokens must successfully access the router."""
    client, identity = connections_client
    identity.id = "user_interactive"
    identity.source = allowed_source

    with patch("app.gateway.routers.user_connections.ComposioClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.api_key = "ak_test"
        mock_instance.list_connected_accounts = AsyncMock(return_value=[])

        res_get = await client.get("/api/connections")
        assert res_get.status_code == 200
        assert res_get.json() == []
        mock_instance.list_connected_accounts.assert_awaited_once_with(user_id="user_interactive")
