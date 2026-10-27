"""SQLAlchemy-backed user MCP connection metadata repository.

Operates against Neon / PostgreSQL (and SQLite in local tests).
"""

from __future__ import annotations

import json
import logging
import time
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nkyel.persistence.user_mcp_connections.model import (
    StoredUserMcpConnection,
    UserMcpConnectionRow,
)

logger = logging.getLogger(__name__)


class UserMcpConnectionRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    @staticmethod
    def _row_to_stored(row: UserMcpConnectionRow) -> StoredUserMcpConnection:
        scopes: list[str] = []
        if row.scopes:
            try:
                scopes = json.loads(row.scopes)
            except Exception:
                scopes = []

        return StoredUserMcpConnection(
            id=row.id,
            user_id=row.user_id,
            provider=row.provider,
            toolkit=row.toolkit,
            connection_id=row.connection_id,
            status=row.status,
            account_identifier=row.account_identifier,
            scopes=scopes,
            auth_link=row.auth_link,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def record_connection(
        self,
        *,
        user_id: str,
        toolkit: str,
        provider: str = "composio",
        connection_id: str | None = None,
        status: str = "INITIATED",
        account_identifier: str | None = None,
        scopes: list[str] | None = None,
        auth_link: str | None = None,
    ) -> StoredUserMcpConnection:
        """Create or update connection record."""
        now = time.time()
        scopes_json = json.dumps(scopes or [])

        async with self._sf() as session:
            stmt = select(UserMcpConnectionRow).where(
                UserMcpConnectionRow.user_id == user_id,
                UserMcpConnectionRow.toolkit == toolkit,
                UserMcpConnectionRow.provider == provider,
            )
            res = await session.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.status = status
                if connection_id:
                    existing.connection_id = connection_id
                if account_identifier:
                    existing.account_identifier = account_identifier
                if scopes:
                    existing.scopes = scopes_json
                if auth_link is not None:
                    existing.auth_link = auth_link
                existing.updated_at = now
                row = existing
            else:
                row = UserMcpConnectionRow(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    provider=provider,
                    toolkit=toolkit,
                    connection_id=connection_id,
                    status=status,
                    account_identifier=account_identifier,
                    scopes=scopes_json,
                    auth_link=auth_link,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)

            await session.commit()
            await session.refresh(row)
            return self._row_to_stored(row)

    async def get_connection(
        self,
        user_id: str,
        toolkit: str,
        provider: str = "composio",
    ) -> StoredUserMcpConnection | None:
        """Get specific connection by user and toolkit."""
        async with self._sf() as session:
            stmt = select(UserMcpConnectionRow).where(
                UserMcpConnectionRow.user_id == user_id,
                UserMcpConnectionRow.toolkit == toolkit,
                UserMcpConnectionRow.provider == provider,
            )
            res = await session.execute(stmt)
            row = res.scalars().first()
            return self._row_to_stored(row) if row else None

    async def list_connections(
        self,
        user_id: str,
        provider: str = "composio",
    ) -> list[StoredUserMcpConnection]:
        """List all connections for the user."""
        async with self._sf() as session:
            stmt = (
                select(UserMcpConnectionRow)
                .where(
                    UserMcpConnectionRow.user_id == user_id,
                    UserMcpConnectionRow.provider == provider,
                )
                .order_by(UserMcpConnectionRow.updated_at.desc())
            )
            res = await session.execute(stmt)
            return [self._row_to_stored(r) for r in res.scalars().all()]

    async def delete_connection(
        self,
        user_id: str,
        toolkit: str,
        provider: str = "composio",
    ) -> bool:
        """Remove connection record for the user and toolkit."""
        async with self._sf() as session:
            stmt = delete(UserMcpConnectionRow).where(
                UserMcpConnectionRow.user_id == user_id,
                UserMcpConnectionRow.toolkit == toolkit,
                UserMcpConnectionRow.provider == provider,
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0
