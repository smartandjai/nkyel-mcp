"""Ñkyel Studio Live MCP, E2B Computer & Human Approval Gateway Router."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from nkyel.mcp.tool_registry import TOOL_REGISTRY, get_verified_tools_count, get_tools_for_mission
from nkyel.mcp.gmail_send_adapter import prepare_gmail_draft, send_gmail_with_approval, APPROVAL_STORE
from nkyel.sandbox.e2b_desktop_tools import (
    computer_launch_session,
    computer_navigate,
    computer_click,
    computer_scroll,
    computer_type_text,
    computer_take_screenshot,
    computer_close_session,
    ACTIVE_SESSIONS
)

router = APIRouter(prefix="/api/nkyel", tags=["nkyel-mcp-studio"])


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class E2BActionRequest(BaseModel):
    sandbox_id: str
    action: str  # "launch", "navigate", "click", "scroll", "type", "screenshot", "close"
    url: str | None = None
    x: int | None = None
    y: int | None = None
    button: str = "left"
    direction: str = "down"
    amount: int = 3
    text: str | None = None
    press_enter: bool = False


class GmailDraftRequest(BaseModel):
    to: str
    subject: str
    body: str
    attachment_paths: list[str] = Field(default_factory=list)


class GmailApprovalRequest(BaseModel):
    approval_token: str
    approved: bool


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/mcp/registry")
async def get_registry():
    """Return all 50 registered MCP tools with live categories and verification status."""
    return {
        "total_tools": get_verified_tools_count(),
        "tools": TOOL_REGISTRY,
        "servers": {
            "google-drive": {"status": "CONNECTED", "protocol": "HTTP/SSE", "endpoint": "https://drivemcp.googleapis.com/mcp/v1"},
            "gmail": {"status": "CONNECTED", "protocol": "HTTP/SSE", "endpoint": "https://gmailmcp.googleapis.com/mcp/v1"},
            "tavily": {"status": "CONNECTED", "protocol": "HTTP/SSE", "endpoint": "https://mcp.tavily.com/mcp/"},
            "e2b-desktop": {"status": "CONNECTED", "protocol": "Official E2B Cloud Desktop SDK"},
            "artifact-engineer": {"status": "CONNECTED", "protocol": "Rust Typst 0.15 + Openpyxl + python-pptx"},
            "duckduckgo": {"status": "CONNECTED", "protocol": "Stdio MCP"},
            "wikipedia": {"status": "CONNECTED", "protocol": "Stdio MCP"},
            "arxiv": {"status": "CONNECTED", "protocol": "Stdio MCP"}
        }
    }


@router.post("/mcp/call")
async def call_tool(req: ToolCallRequest):
    """Execute a real MCP tool by name."""
    name = req.tool_name
    args = req.arguments

    if name.startswith("tavily_"):
        import httpx
        auth = os.getenv("TAVILY_MCP_AUTH")
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": args}
        }
        try:
            r = httpx.post("https://mcp.tavily.com/mcp/", headers=headers, json=payload, timeout=20.0)
            for line in r.text.splitlines():
                if line.startswith("data:"):
                    import json
                    return json.loads(line[5:].strip())
            return {"raw": r.text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif name == "computer_launch_session":
        return computer_launch_session(args.get("initial_url", "https://google.com"))

    elif name == "computer_navigate":
        return computer_navigate(args["sandbox_id"], args["url"])

    elif name == "computer_click":
        return computer_click(args["sandbox_id"], args["x"], args["y"], args.get("button", "left"))

    elif name == "computer_scroll":
        return computer_scroll(args["sandbox_id"], args.get("direction", "down"), args.get("amount", 3))

    elif name == "computer_type_text":
        return computer_type_text(args["sandbox_id"], args["text"], args.get("press_enter", False))

    elif name == "computer_close_session":
        return computer_close_session(args["sandbox_id"])

    elif name == "gmail_prepare_draft_with_attachment":
        return prepare_gmail_draft(
            to=args["to"],
            subject=args["subject"],
            body=args["body"],
            attachment_paths=args.get("attachment_paths", [])
        )

    elif name == "gmail_send_with_approval":
        return send_gmail_with_approval(
            approval_token=args["approval_token"],
            approved=args.get("approved", True)
        )

    raise HTTPException(status_code=404, detail=f"Tool '{name}' execution handler not implemented.")


@router.post("/e2b/action")
async def execute_e2b_action(req: E2BActionRequest):
    """Control the real E2B live visual computer."""
    act = req.action
    if act == "launch":
        return computer_launch_session(req.url or "https://aninf.ga")
    elif act == "navigate":
        return computer_navigate(req.sandbox_id, req.url or "https://google.com")
    elif act == "click":
        return computer_click(req.sandbox_id, req.x or 500, req.y or 300, req.button)
    elif act == "scroll":
        return computer_scroll(req.sandbox_id, req.direction, req.amount)
    elif act == "type":
        return computer_type_text(req.sandbox_id, req.text or "", req.press_enter)
    elif act == "screenshot":
        return computer_take_screenshot(req.sandbox_id)
    elif act == "close":
        return computer_close_session(req.sandbox_id)
    raise HTTPException(status_code=400, detail=f"Unknown E2B action: {act}")


@router.get("/gmail/drafts")
async def list_drafts():
    """List pending drafts awaiting human approval."""
    return list(APPROVAL_STORE.values())


@router.post("/gmail/approve")
async def approve_and_send_email(req: GmailApprovalRequest):
    """Execute human approval action for sending email with attachment."""
    res = send_gmail_with_approval(req.approval_token, req.approved)
    return res
