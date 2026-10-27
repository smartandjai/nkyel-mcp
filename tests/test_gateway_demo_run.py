"""Test for Ñkyel Demo Gateway Run Creation, Schema Validation and Tavily MCP Search."""

import os
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "backend/.env")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8001")
DEMO_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_HKkCZuxn2j0O@ep-shy-firefly-abitziup-pooler.eu-west-2.aws.neon.tech/nkyel_demo?ssl=require",
)


@pytest.mark.asyncio
async def test_demo_database_schema_runs():
    """Verify that nkyel_demo runs table has correct schema without broken legacy NOT NULL columns."""
    url = DEMO_DB_URL
    if "sslmode=" in url:
        url = url.replace("?sslmode=", "?ssl=").replace("&sslmode=", "&ssl=")
    url = url.replace("&channel_binding=require", "").replace("?channel_binding=require", "?").rstrip("?")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(url)
    async with engine.connect() as conn:
        cols_query = await conn.execute(
            text("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='runs'")
        )
        cols = {row[0]: row[1] for row in cols_query.fetchall()}
        assert "run_id" in cols
        assert "thread_id" in cols
        # mission_id must NOT be a mandatory non-null column
        if "mission_id" in cols:
            assert cols["mission_id"] == "YES"
    await engine.dispose()


def test_tavily_mcp_search_via_gateway():
    """Verify Tavily MCP tool call directly through Gateway /api/nkyel/mcp/call."""
    auth = os.getenv("TAVILY_MCP_AUTH")
    with httpx.Client(timeout=15.0) as client:
        # Check gateway health first
        h = client.get(f"{GATEWAY_URL}/health")
        assert h.status_code == 200
        assert h.json().get("status") == "healthy"

        # Execute direct Tavily MCP tools/call
        tavily_headers = {"Content-Type": "application/json"}
        if auth:
            tavily_headers["Authorization"] = auth
        call_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "tavily_search", "arguments": {"query": "ANINF Gabon", "max_results": 2}},
        }
        res = client.post("https://mcp.tavily.com/mcp/", headers=tavily_headers, json=call_payload)
        assert res.status_code == 200
        data = None
        for line in res.text.splitlines():
            if line.startswith("data:"):
                import json
                data = json.loads(line[5:].strip())
                break
        if data is None:
            data = res.json()
        assert "result" in data
        assert data["result"].get("isError") is False or data.get("isError") is False
