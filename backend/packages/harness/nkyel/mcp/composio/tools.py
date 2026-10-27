"""Composio Sessions MCP Tools & Dynamic Discovery for DeerFlow Agent.

Allows users to connect external apps (Gmail, Google Drive, GitHub, Notion)
with user consent and OAuth handled securely by Composio.
Guards all tool calls so User A cannot access User B's connections or tools.
"""

from __future__ import annotations

import functools
import logging
from typing import Any

from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool, ToolException

from nkyel.mcp.composio.client import ComposioClient
from nkyel.runtime.user_context import resolve_runtime_user_id
from nkyel.tools.sync import make_sync_tool_wrapper

logger = logging.getLogger(__name__)

# Cached client instance
_composio_client: ComposioClient | None = None


def get_composio_client() -> ComposioClient:
    global _composio_client
    if _composio_client is None:
        _composio_client = ComposioClient()
    return _composio_client


# ─── User-Consent & Connection Management Tools ──────────────────────────────


@tool("composio_check_connection")
def composio_check_connection_tool(
    runtime: ToolRuntime,
    toolkit: str,
) -> dict[str, Any]:
    """Check if the user has an active, authorized connection for an external application.

    Args:
        toolkit: The application name to check (e.g. 'gmail', 'google_drive', 'github', 'notion').
    """
    user_id = resolve_runtime_user_id(runtime)
    toolkit_clean = toolkit.lower().strip()
    client = get_composio_client()

    try:
        # Run async list in thread/sync wrapper
        accounts = make_sync_tool_wrapper(client.list_connected_accounts, "list_accounts")(user_id=user_id, toolkit=toolkit_clean)
        active = [acc for acc in accounts if acc.status == "ACTIVE" and acc.toolkit == toolkit_clean]
        if active:
            acc = active[0]
            return {
                "toolkit": toolkit_clean,
                "connected": True,
                "status": "ACTIVE",
                "account_identifier": acc.account_identifier,
                "connection_id": acc.connection_id,
                "scopes": acc.scopes,
                "observation": f"{toolkit_clean.title()} is connected and authorized for your account ({acc.account_identifier or acc.connection_id}).",
            }
        return {
            "toolkit": toolkit_clean,
            "connected": False,
            "status": "NOT_CONNECTED",
            "observation": f"{toolkit_clean.title()} is not connected. Use composio_connect_app to generate an authorization link.",
        }
    except Exception as e:
        logger.error(f"Error checking connection for {toolkit}: {e}")
        return {
            "toolkit": toolkit_clean,
            "connected": False,
            "status": "ERROR",
            "error": str(e),
            "observation": f"Could not check connection for {toolkit_clean}: {e}",
        }


@tool("composio_connect_app")
def composio_connect_app_tool(
    runtime: ToolRuntime,
    toolkit: str,
) -> dict[str, Any]:
    """Request user authorization to connect an external app (e.g. 'gmail', 'google_drive').

    Generates a secure provider authorization link for the authenticated Clerk user.
    The user clicks this link to approve OAuth permissions on the provider's official page.

    Args:
        toolkit: Application name to connect (e.g. 'gmail', 'google_drive', 'github', 'notion').
    """
    user_id = resolve_runtime_user_id(runtime)
    toolkit_clean = toolkit.lower().strip()
    client = get_composio_client()

    try:
        auth_link = make_sync_tool_wrapper(client.get_authorization_link, "get_auth_link")(user_id=user_id, toolkit=toolkit_clean)
        return {
            "toolkit": toolkit_clean,
            "status": "AWAITING_USER_AUTHORIZATION",
            "authorization_url": auth_link.redirect_url,
            "connection_id": auth_link.connection_id,
            "session_id": auth_link.session_id,
            "observation": (f"Please authorize access to {toolkit_clean.title()} by opening this link: {auth_link.redirect_url}\n\nOnce you have granted access on Google/the provider page, I will be able to perform your request."),
        }
    except Exception as e:
        logger.error(f"Failed to generate connect link for {toolkit}: {e}")
        return {
            "toolkit": toolkit_clean,
            "status": "ERROR",
            "error": str(e),
            "observation": f"Failed to generate authorization link for {toolkit_clean}: {e}",
        }


@tool("composio_disconnect_app")
def composio_disconnect_app_tool(
    runtime: ToolRuntime,
    toolkit: str,
) -> dict[str, Any]:
    """Disconnect and revoke access to an external application.

    Args:
        toolkit: Application name to disconnect (e.g. 'gmail', 'google_drive').
    """
    user_id = resolve_runtime_user_id(runtime)
    toolkit_clean = toolkit.lower().strip()
    client = get_composio_client()

    try:
        accounts = make_sync_tool_wrapper(client.list_connected_accounts, "list_accounts")(user_id=user_id, toolkit=toolkit_clean)
        deleted_count = 0
        for acc in accounts:
            if acc.toolkit == toolkit_clean and acc.connection_id:
                ok = make_sync_tool_wrapper(client.delete_connected_account, "delete_account")(acc.connection_id)
                if ok:
                    deleted_count += 1

        return {
            "toolkit": toolkit_clean,
            "success": True,
            "disconnected_count": deleted_count,
            "observation": f"Successfully disconnected {toolkit_clean.title()}.",
        }
    except Exception as e:
        logger.error(f"Failed to disconnect {toolkit}: {e}")
        return {
            "toolkit": toolkit_clean,
            "success": False,
            "error": str(e),
            "observation": f"Could not disconnect {toolkit_clean}: {e}",
        }


COMPOSIO_MANAGEMENT_TOOLS: list[BaseTool] = [
    composio_check_connection_tool,
    composio_connect_app_tool,
    composio_disconnect_app_tool,
]


# ─── Dynamic Session MCP Discovery & User Isolation Guard ─────────────────────


def _resolve_caller_user_id(runtime: Any = None) -> str:
    """Resolve calling user id from runtime object, attributes, or task-local ContextVar."""
    if runtime is not None:
        user_id = getattr(runtime, "user_id", None)
        if user_id:
            return str(user_id)
        resolved = resolve_runtime_user_id(runtime)
        if resolved and resolved != "default":
            return resolved
    return resolve_runtime_user_id(None)


def _guard_user_tool(tool_instance: BaseTool, owner_user_id: str) -> BaseTool:
    """Wraps MCP tool to ensure only the owner Clerk user can invoke it."""
    orig_coro = tool_instance.coroutine
    orig_func = tool_instance.func

    if orig_coro is not None:

        @functools.wraps(orig_coro)
        async def guarded_coro(*args: Any, **kwargs: Any) -> Any:
            runtime = kwargs.get("runtime")
            current_user = _resolve_caller_user_id(runtime)
            if current_user != owner_user_id:
                raise ToolException(f"Access denied: this tool belongs to user '{owner_user_id}', not '{current_user}'.")
            return await orig_coro(*args, **kwargs)

        guarded_sync = make_sync_tool_wrapper(guarded_coro, tool_instance.name)
        return tool_instance.model_copy(update={"coroutine": guarded_coro, "func": guarded_sync})

    elif orig_func is not None:

        @functools.wraps(orig_func)
        def guarded_func(*args: Any, **kwargs: Any) -> Any:
            runtime = kwargs.get("runtime")
            current_user = _resolve_caller_user_id(runtime)
            if current_user != owner_user_id:
                raise ToolException(f"Access denied: this tool belongs to user '{owner_user_id}', not '{current_user}'.")
            return orig_func(*args, **kwargs)

        return tool_instance.model_copy(update={"func": guarded_func})

    return tool_instance


async def _discover_composio_session_tools(user_id: str) -> list[BaseTool]:
    """Query user's active accounts, get MCP session, and load tools via langchain_mcp_adapters."""
    client = get_composio_client()
    if not client.api_key:
        return []

    try:
        accounts = await client.list_connected_accounts(user_id=user_id)
        active_toolkits = list({acc.toolkit for acc in accounts if acc.status == "ACTIVE" and acc.toolkit})
        if not active_toolkits:
            logger.debug(f"No active connected accounts for user {user_id}")
            return []

        logger.info(f"User {user_id} has active toolkits: {active_toolkits}. Initializing Composio MCP session...")
        session_info = await client.create_or_get_session(user_id=user_id, toolkits=active_toolkits)

        from langchain_mcp_adapters.client import MultiServerMCPClient

        server_name = f"composio_{user_id}"
        server_config = {
            server_name: {
                "transport": "http",
                "url": session_info.mcp_url,
                "headers": session_info.mcp_headers,
            }
        }
        mcp_client = MultiServerMCPClient(server_config)
        raw_tools = await mcp_client.get_tools(server_name=server_name)

        # Wrap tools with strict user isolation
        guarded = [_guard_user_tool(t, user_id) for t in raw_tools]
        logger.info(f"Loaded {len(guarded)} user-scoped Composio MCP tools for user {user_id}: {[t.name for t in guarded]}")
        return guarded
    except Exception as e:
        logger.warning(f"Could not load Composio session tools for user {user_id}: {e}")
        return []


def get_composio_session_mcp_tools(user_id: str) -> list[BaseTool]:
    """Synchronous discovery entry point for DeerFlow agent assembly."""
    if not user_id or user_id == "default":
        return []
    try:
        runner = make_sync_tool_wrapper(_discover_composio_session_tools, "composio_mcp_discovery")
        return runner(user_id)
    except Exception as e:
        logger.warning(f"Failed to fetch Composio session tools for {user_id}: {e}")
        return []
