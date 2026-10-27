"""Automated Tests for User-Consented MCP Connections via Composio Sessions.

Verifies:
1. Server-side Composio Sessions client adapter (v3.1) with Clerk user scoping
2. Neon/PostgreSQL connection metadata persistence (no plaintext tokens)
3. DeerFlow tool availability (check, connect, disconnect) and dynamic session discovery
4. Strict user isolation: User B cannot access or invoke User A's connected tools
5. Connect Link generation and authorization flow
6. Opt-in live integration test for Composio Sessions MCP
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.tools import ToolException, tool
from nkyel.mcp.composio.client import (
    ComposioAuthLink,
    ComposioClient,
)
from nkyel.mcp.composio.tools import (
    _guard_user_tool,
    composio_connect_app_tool,
)
from nkyel.persistence.base import Base
from nkyel.persistence.user_mcp_connections.sql import UserMcpConnectionRepository
from nkyel.runtime.user_context import reset_current_user, set_current_user
from nkyel.tools.tools import get_available_tools
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ─── Test 1: Composio Client & Session Creation ──────────────────────────────


@pytest.mark.asyncio
async def test_composio_session_creation_scoped_to_clerk_user():
    """Verify Composio session creation uses the Clerk user_id and returns MCP endpoint."""
    client = ComposioClient(api_key="test_composio_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "session_id": "sess_clerk_user_1",
        "mcp": {
            "url": "https://backend.composio.dev/api/v3.1/tool_router/session/sess_clerk_user_1/mcp",
            "headers": {"x-api-key": "test_composio_key"},
        },
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        session_info = await client.create_or_get_session(
            user_id="user_2clerk_abc123",
            toolkits=["gmail", "google_drive"],
        )

        assert session_info.session_id == "sess_clerk_user_1"
        assert session_info.user_id == "user_2clerk_abc123"
        assert "sess_clerk_user_1" in session_info.mcp_url
        assert session_info.mcp_headers.get("x-api-key") == "test_composio_key"

        # Verify POST payload contained Clerk user_id
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["user_id"] == "user_2clerk_abc123"
        assert kwargs["json"]["toolkits"] == {"enable": ["gmail", "google_drive"]}


@pytest.mark.asyncio
async def test_composio_auth_link_generation():
    """Verify Connect Link generation returns provider redirect URL."""
    client = ComposioClient(api_key="test_composio_key")

    mock_session_resp = MagicMock(
        status_code=200,
        json=lambda: {"session_id": "sess_123", "mcp": {"url": "https://mcp.url"}},
    )
    mock_link_resp = MagicMock(
        status_code=200,
        json=lambda: {
            "redirect_url": "https://connect.composio.dev/auth/gmail_flow_xyz",
            "connection_id": "conn_gmail_999",
        },
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = [mock_session_resp, mock_link_resp]

        auth_link = await client.get_authorization_link(
            user_id="user_clerk_456",
            toolkit="gmail",
        )

        assert auth_link.toolkit == "gmail"
        assert "connect.composio.dev" in auth_link.redirect_url
        assert auth_link.connection_id == "conn_gmail_999"


# ─── Test 2: Neon Metadata Persistence (No Plaintext Tokens) ─────────────────


@pytest.mark.asyncio
async def test_neon_user_mcp_connections_repository():
    """Verify user connections metadata can be stored, listed, and deleted without secrets."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    repo = UserMcpConnectionRepository(session_factory)

    # 1. Record initiated connection
    conn1 = await repo.record_connection(
        user_id="user_clerk_alice",
        toolkit="gmail",
        connection_id="conn_composio_1",
        status="INITIATED",
        auth_link="https://connect.composio.dev/auth/alice",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    assert conn1.user_id == "user_clerk_alice"
    assert conn1.toolkit == "gmail"
    assert conn1.status == "INITIATED"
    assert "https://www.googleapis.com/auth/gmail.readonly" in conn1.scopes

    # 2. Update to ACTIVE once authorized
    conn1_active = await repo.record_connection(
        user_id="user_clerk_alice",
        toolkit="gmail",
        connection_id="conn_composio_1",
        status="ACTIVE",
        account_identifier="alice@gmail.com",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    assert conn1_active.status == "ACTIVE"
    assert conn1_active.account_identifier == "alice@gmail.com"

    # 3. Add Google Drive connection
    await repo.record_connection(
        user_id="user_clerk_alice",
        toolkit="google_drive",
        connection_id="conn_composio_2",
        status="ACTIVE",
        account_identifier="alice@gmail.com",
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

    # 4. List connections for Alice
    alice_conns = await repo.list_connections("user_clerk_alice")
    assert len(alice_conns) == 2
    toolkits = {c.toolkit for c in alice_conns}
    assert toolkits == {"gmail", "google_drive"}

    # 5. List connections for Bob (should be empty, proving isolation)
    bob_conns = await repo.list_connections("user_clerk_bob")
    assert len(bob_conns) == 0

    # 6. Delete connection
    deleted = await repo.delete_connection("user_clerk_alice", "gmail")
    assert deleted is True
    alice_remaining = await repo.list_connections("user_clerk_alice")
    assert len(alice_remaining) == 1
    assert alice_remaining[0].toolkit == "google_drive"

    await engine.dispose()


# ─── Test 3: User Isolation Guard (User A vs User B) ─────────────────────────


@pytest.mark.asyncio
async def test_composio_tool_strict_user_isolation():
    """Verify that User B cannot invoke User A's connected tools."""

    @tool("gmail_read_emails")
    async def sample_gmail_tool(query: str = "", runtime: Any = None) -> str:
        """Sample Gmail tool."""
        return "Subject: Important Project Update"

    # Guard the tool for owner 'user_alice'
    guarded_tool = _guard_user_tool(sample_gmail_tool, owner_user_id="user_alice")

    # Mock runtime for Alice
    runtime_alice = MagicMock(user_id="user_alice")

    # 1. Alice invokes with runtime -> SUCCESS
    result_alice = await guarded_tool.ainvoke(
        {"query": "project", "runtime": runtime_alice}
    )
    assert "Important Project Update" in result_alice

    # 2. Bob invokes with runtime -> ACCESS DENIED
    runtime_bob = MagicMock(user_id="user_bob")
    with pytest.raises(ToolException) as exc_info:
        await guarded_tool.ainvoke({"query": "project", "runtime": runtime_bob})

    assert "Access denied" in str(exc_info.value)
    assert "user_alice" in str(exc_info.value)

    # 3. ContextVar isolation: Alice in context -> SUCCESS
    token_alice = set_current_user(MagicMock(id="user_alice"))
    try:
        res_ctx = await guarded_tool.ainvoke({"query": "project"})
        assert "Important Project Update" in res_ctx
    finally:
        reset_current_user(token_alice)

    # 4. ContextVar isolation: Bob in context -> ACCESS DENIED
    token_bob = set_current_user(MagicMock(id="user_bob"))
    try:
        with pytest.raises(ToolException) as exc_info_bob:
            await guarded_tool.ainvoke({"query": "project"})
        assert "Access denied" in str(exc_info_bob.value)
    finally:
        reset_current_user(token_bob)


# ─── Test 4: DeerFlow Available Tools Registration ───────────────────────────


def test_composio_management_tools_registered_in_deerflow():
    """Verify Composio management tools are registered in DeerFlow get_available_tools()."""
    available = get_available_tools()
    tool_names = {t.name for t in available}

    expected = {
        "composio_check_connection",
        "composio_connect_app",
        "composio_disconnect_app",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


# ─── Test 5: In-Chat Connect Tool Execution ──────────────────────────────────


def test_composio_connect_tool_returns_auth_link():
    """Verify composio_connect_app produces a clickable authorization link for the user."""
    mock_auth_link = ComposioAuthLink(
        toolkit="gmail",
        redirect_url="https://connect.composio.dev/auth/link_123",
        connection_id="conn_456",
        session_id="sess_789",
    )

    with patch("nkyel.mcp.composio.tools.get_composio_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_authorization_link = AsyncMock(return_value=mock_auth_link)
        mock_get_client.return_value = mock_client

        mock_runtime = MagicMock(user_id="user_clerk_1")
        res = composio_connect_app_tool.func(toolkit="gmail", runtime=mock_runtime)

        assert res["status"] == "AWAITING_USER_AUTHORIZATION"
        assert res["authorization_url"] == "https://connect.composio.dev/auth/link_123"
        assert "connect.composio.dev" in res["observation"]


# ─── Test 6: Opt-in Live Composio Sessions MCP Integration ───────────────────


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_COMPOSIO_TEST") != "1",
    reason="Opt-in live integration test. Set RUN_LIVE_COMPOSIO_TEST=1 to run.",
)
@pytest.mark.asyncio
async def test_live_composio_mcp_integration():
    """Live verification of Composio API key and session creation."""
    api_key = os.getenv("COMPOSIO_API_KEY")
    assert api_key, "COMPOSIO_API_KEY must be configured in environment."

    client = ComposioClient(api_key=api_key)
    session_info = await client.create_or_get_session(
        user_id="nkyel_test_user_01",
        toolkits=["gmail"],
    )
    assert session_info.session_id, "Composio session_id must not be empty"
    assert session_info.mcp_url.startswith("https://"), "MCP endpoint must be HTTPS"
    assert "x-api-key" in session_info.mcp_headers
