"""ORM model for user MCP connections metadata stored in Neon/Postgres.

Records user-consented integration handles, provider names, statuses, and scopes.
Never stores third-party access or refresh tokens in plaintext.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from sqlalchemy import Double, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nkyel.persistence.base import Base


class UserMcpConnectionRow(Base):
    __tablename__ = "user_mcp_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="composio")
    toolkit: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    connection_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="INITIATED")  # INITIATED, ACTIVE, EXPIRED, REVOKED
    account_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-serialized list of scopes
    auth_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[float] = mapped_column(Double, nullable=False, default=time.time)
    updated_at: Mapped[float] = mapped_column(Double, nullable=False, default=time.time)


@dataclass(frozen=True)
class StoredUserMcpConnection:
    id: str
    user_id: str
    provider: str
    toolkit: str
    connection_id: str | None
    status: str
    account_identifier: str | None
    scopes: list[str]
    auth_link: str | None
    created_at: float
    updated_at: float
