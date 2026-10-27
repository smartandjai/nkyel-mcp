"""User-Consented MCP Application Connections Router.

Enables Clerk-authenticated users to view, authorize, and disconnect external
integrations (Gmail, Google Drive, GitHub, Notion) via Composio Sessions.
Does NOT store or expose third-party access or refresh tokens in plaintext.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.gateway.deps import get_authenticated_user
from nkyel.mcp.composio.client import ComposioClient
from nkyel.runtime.user_context import get_effective_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/connections", tags=["connections"])


class AuthorizeConnectionRequest(BaseModel):
    toolkit: str = Field(..., description="Application name to connect (e.g. 'gmail', 'google_drive')")
    callback_url: str | None = Field(None, description="Optional redirect URL after user approval")


class ConnectionResponse(BaseModel):
    toolkit: str
    status: str
    connected: bool
    account_identifier: str | None = None
    connection_id: str | None = None
    scopes: list[str] = Field(default_factory=list)


class AuthorizeConnectionResponse(BaseModel):
    toolkit: str
    authorization_url: str
    connection_id: str | None = None
    session_id: str | None = None
    status: str = "AWAITING_USER_AUTHORIZATION"


@router.get("", response_model=list[ConnectionResponse])
async def list_user_connections(
    request: Request,
    user: Any = Depends(get_authenticated_user),
) -> list[ConnectionResponse]:
    """List external applications and connection statuses for the current user."""
    user_id = str(user.id) if user else get_effective_user_id()
    client = ComposioClient()
    if not client.api_key:
        return []

    try:
        accounts = await client.list_connected_accounts(user_id=user_id)
        return [
            ConnectionResponse(
                toolkit=acc.toolkit,
                status=acc.status,
                connected=(acc.status == "ACTIVE"),
                account_identifier=acc.account_identifier,
                connection_id=acc.connection_id,
                scopes=acc.scopes,
            )
            for acc in accounts
        ]
    except Exception as e:
        logger.error(f"Failed to list connections for user {user_id}: {e}")
        return []


@router.post("/authorize", response_model=AuthorizeConnectionResponse)
async def authorize_user_connection(
    req: AuthorizeConnectionRequest,
    request: Request,
    user: Any = Depends(get_authenticated_user),
) -> AuthorizeConnectionResponse:
    """Generate a secure Connect Link for user authorization."""
    user_id = str(user.id) if user else get_effective_user_id()
    client = ComposioClient()
    if not client.api_key:
        raise HTTPException(status_code=500, detail="COMPOSIO_API_KEY is not configured on Gateway.")

    toolkit_clean = req.toolkit.lower().strip()
    try:
        auth_link = await client.get_authorization_link(
            user_id=user_id,
            toolkit=toolkit_clean,
            callback_url=req.callback_url,
        )
        return AuthorizeConnectionResponse(
            toolkit=toolkit_clean,
            authorization_url=auth_link.redirect_url,
            connection_id=auth_link.connection_id,
            session_id=auth_link.session_id,
        )
    except Exception as e:
        logger.error(f"Failed to generate authorization link for {req.toolkit}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to initiate authorization: {e}")


@router.delete("/{toolkit}")
async def disconnect_user_connection(
    toolkit: str,
    request: Request,
    user: Any = Depends(get_authenticated_user),
) -> dict[str, Any]:
    """Disconnect and revoke access to an external application."""
    user_id = str(user.id) if user else get_effective_user_id()
    client = ComposioClient()
    if not client.api_key:
        raise HTTPException(status_code=500, detail="COMPOSIO_API_KEY is not configured on Gateway.")

    toolkit_clean = toolkit.lower().strip()
    try:
        accounts = await client.list_connected_accounts(user_id=user_id, toolkit=toolkit_clean)
        deleted = 0
        for acc in accounts:
            if acc.toolkit == toolkit_clean and acc.connection_id:
                ok = await client.delete_connected_account(acc.connection_id)
                if ok:
                    deleted += 1

        return {"toolkit": toolkit_clean, "success": True, "disconnected_count": deleted}
    except Exception as e:
        logger.error(f"Failed to disconnect {toolkit}: {e}")
        raise HTTPException(status_code=502, detail=f"Disconnection failed: {e}")
