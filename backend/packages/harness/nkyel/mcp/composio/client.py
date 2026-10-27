"""Composio Sessions REST API Client (v3.1).

Handles user-scoped sessions, connect links, and connected account lifecycles.
Never handles raw OAuth secrets; uses Composio hosted session endpoints.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

COMPOSIO_API_BASE_URL = os.getenv("COMPOSIO_API_BASE_URL", "https://backend.composio.dev/api/v3.1")


@dataclass(frozen=True)
class ComposioSessionInfo:
    session_id: str
    user_id: str
    mcp_url: str
    mcp_headers: dict[str, str]


@dataclass(frozen=True)
class ComposioAuthLink:
    toolkit: str
    redirect_url: str
    connection_id: str | None
    session_id: str


@dataclass(frozen=True)
class ComposioAccountInfo:
    connection_id: str
    user_id: str
    toolkit: str
    status: str  # ACTIVE, INITIATED, EXPIRED, etc.
    account_identifier: str | None
    scopes: list[str]
    created_at: str | None


class ComposioClient:
    """Async client for Composio Sessions and Connected Accounts."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY", "")
        self.base_url = COMPOSIO_API_BASE_URL.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ValueError("COMPOSIO_API_KEY is not configured in environment.")
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_or_get_session(
        self,
        user_id: str,
        toolkits: list[str] | None = None,
        callback_url: str | None = None,
    ) -> ComposioSessionInfo:
        """Create or retrieve a user-scoped tool-router session exposing an MCP endpoint."""
        url = f"{self.base_url}/tool_router/session"
        payload: dict[str, Any] = {
            "user_id": user_id,
            "manage_connections": {
                "enable": True,
                "callback_url": callback_url or "https://nkyel.smartandjai.com/chat",
            },
        }
        if toolkits:
            payload["toolkits"] = {"enable": toolkits}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            if resp.status_code >= 400:
                logger.error(f"Failed to create Composio session for user {user_id}: {resp.status_code} {resp.text}")
                resp.raise_for_status()

            data = resp.json()
            session_id = data.get("session_id") or data.get("id") or ""
            mcp_data = data.get("mcp") or {}
            mcp_url = mcp_data.get("url") or f"{self.base_url}/tool_router/session/{session_id}/mcp"
            mcp_headers = mcp_data.get("headers") or {"x-api-key": self.api_key}

            return ComposioSessionInfo(
                session_id=session_id,
                user_id=user_id,
                mcp_url=mcp_url,
                mcp_headers=mcp_headers,
            )

    async def get_authorization_link(
        self,
        user_id: str,
        toolkit: str,
        callback_url: str | None = None,
    ) -> ComposioAuthLink:
        """Generate a secure Connect Link for the user to authorize a provider."""
        session = await self.create_or_get_session(user_id=user_id, toolkits=[toolkit], callback_url=callback_url)
        url = f"{self.base_url}/tool_router/session/{session.session_id}/link"
        payload = {"toolkit": toolkit}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            if resp.status_code >= 400:
                logger.error(f"Failed to get authorization link for toolkit {toolkit}: {resp.status_code} {resp.text}")
                resp.raise_for_status()

            data = resp.json()
            redirect_url = data.get("redirect_url") or data.get("url") or ""
            connection_id = data.get("connection_id") or data.get("id")

            return ComposioAuthLink(
                toolkit=toolkit,
                redirect_url=redirect_url,
                connection_id=str(connection_id) if connection_id else None,
                session_id=session.session_id,
            )

    async def list_connected_accounts(
        self,
        user_id: str,
        toolkit: str | None = None,
    ) -> list[ComposioAccountInfo]:
        """List active and initiated connected accounts for the given user."""
        url = f"{self.base_url}/connected_accounts"
        params: dict[str, str] = {"user_ids": user_id}
        if toolkit:
            params["toolkit"] = toolkit

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            if resp.status_code >= 400:
                logger.warning(f"Could not list connected accounts for user {user_id}: {resp.status_code}")
                return []

            data = resp.json()
            items = data.get("items") or (data if isinstance(data, list) else [])
            accounts: list[ComposioAccountInfo] = []
            for item in items:
                acc_user_id = item.get("user_id") or item.get("userId") or user_id
                acc_toolkit = item.get("toolkit") or item.get("app_unique_id") or item.get("appName") or ""
                status = (item.get("status") or "ACTIVE").upper()
                conn_id = str(item.get("id") or item.get("connection_id") or "")
                params_obj = item.get("params") or {}
                ident = params_obj.get("email") or params_obj.get("username") or item.get("account_identifier")
                scopes = item.get("scopes") or []

                accounts.append(
                    ComposioAccountInfo(
                        connection_id=conn_id,
                        user_id=acc_user_id,
                        toolkit=acc_toolkit.lower(),
                        status=status,
                        account_identifier=ident,
                        scopes=scopes if isinstance(scopes, list) else [],
                        created_at=item.get("created_at"),
                    )
                )

            return accounts

    async def delete_connected_account(self, connection_id: str) -> bool:
        """Revoke and delete a connected account by its Composio connection ID."""
        url = f"{self.base_url}/connected_accounts/{connection_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.delete(url, headers=self._headers())
            return resp.status_code in (200, 204)
