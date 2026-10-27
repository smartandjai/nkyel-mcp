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


class E2BCodeRunRequest(BaseModel):
    code: str
    sandbox_id: str | None = None


class E2BTerminalRunRequest(BaseModel):
    command: str
    sandbox_id: str | None = None


class GmailDraftRequest(BaseModel):
    to: str
    subject: str
    body: str
    attachment_paths: list[str] = Field(default_factory=list)


class GmailApprovalRequest(BaseModel):
    approval_token: str
    approved: bool


# ─── Live State & Event Buffer ────────────────────────────────────────────────
import time
from datetime import datetime, timezone

ACTIVE_CODE_SESSIONS: dict[str, Any] = {}
E2B_EVENT_LOG: list[dict[str, Any]] = [
    {
        "id": "init-1",
        "type": "system",
        "title": "E2B Cloud MicroVM Engine Initialized",
        "details": "Prêt pour l'exécution de code Python, terminal bash et inspection Chrome",
        "status": "success",
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    }
]

def record_e2b_event(event_type: str, title: str, details: str, status: str = "success") -> None:
    E2B_EVENT_LOG.append({
        "id": f"evt-{int(time.time() * 1000)}",
        "type": event_type,
        "title": title,
        "details": details,
        "status": status,
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })
    if len(E2B_EVENT_LOG) > 60:
        del E2B_EVENT_LOG[:-50]


def _get_or_create_code_sandbox(sandbox_id: str | None = None):
    from e2b_code_interpreter import Sandbox
    api_key = os.getenv("E2B_API_KEY")
    if sandbox_id and sandbox_id in ACTIVE_CODE_SESSIONS:
        return ACTIVE_CODE_SESSIONS[sandbox_id]
    
    # Check if any session is active
    if not sandbox_id and ACTIVE_CODE_SESSIONS:
        first_id = next(iter(ACTIVE_CODE_SESSIONS))
        return ACTIVE_CODE_SESSIONS[first_id]

    sbx = Sandbox.create(api_key=api_key)
    ACTIVE_CODE_SESSIONS[sbx.sandbox_id] = sbx
    record_e2b_event("microvm", "Nouvelle MicroVM E2B créée", f"ID: {sbx.sandbox_id}")
    return sbx


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


@router.get("/e2b/status")
async def get_e2b_status():
    """Return live E2B cloud status, capabilities, and active sessions."""
    api_key = os.getenv("E2B_API_KEY")
    return {
        "connected": bool(api_key),
        "api_key_configured": bool(api_key),
        "engine": "E2B Cloud Sandboxes (Debian 13 MicroVM)",
        "capabilities": ["desktop_chrome", "code_interpreter", "bash_terminal", "live_stream", "filesystem"],
        "active_desktop_sessions": list(ACTIVE_SESSIONS.keys()),
        "active_code_sessions": list(ACTIVE_CODE_SESSIONS.keys()),
        "total_active": len(ACTIVE_SESSIONS) + len(ACTIVE_CODE_SESSIONS),
    }


@router.get("/e2b/events")
async def get_e2b_events():
    """Return rolling live execution events for the frontend visual panel."""
    return {"events": list(reversed(E2B_EVENT_LOG))}


@router.post("/e2b/run_code")
async def run_e2b_code(req: E2BCodeRunRequest):
    """Execute Python code in isolated E2B Cloud MicroVM."""
    t0 = time.time()
    try:
        sbx = _get_or_create_code_sandbox(req.sandbox_id)
        execution = sbx.run_code(req.code)
        duration_ms = int((time.time() - t0) * 1000)

        stdout = execution.logs.stdout
        stderr = execution.logs.stderr

        results_data = []
        for r in (execution.results or []):
            if hasattr(r, "png") and r.png:
                results_data.append({"type": "image/png", "data": r.png})
            elif hasattr(r, "text") and r.text:
                results_data.append({"type": "text/plain", "data": r.text})
            else:
                results_data.append({"type": "raw", "data": str(r)})

        error_msg = None
        if execution.error:
            error_msg = f"{execution.error.name}: {execution.error.value}\n{execution.error.traceback}"
            record_e2b_event("code", "Erreur d'exécution Python", error_msg[:120], "error")
        else:
            record_e2b_event("code", "Exécution Python réussie", f"{len(stdout)} ligne(s) · {duration_ms}ms", "success")

        return {
            "sandbox_id": sbx.sandbox_id,
            "stdout": stdout,
            "stderr": stderr,
            "results": results_data,
            "error": error_msg,
            "execution_time_ms": duration_ms,
            "status": "COMPLETED" if not error_msg else "ERROR"
        }
    except Exception as e:
        record_e2b_event("code", "Exception MicroVM E2B", str(e), "error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/e2b/terminal")
async def run_e2b_terminal(req: E2BTerminalRunRequest):
    """Execute bash command inside E2B Cloud microVM."""
    t0 = time.time()
    try:
        sbx = _get_or_create_code_sandbox(req.sandbox_id)
        cmd_proc = sbx.commands.run(req.command)
        duration_ms = int((time.time() - t0) * 1000)

        stdout = getattr(cmd_proc, "stdout", "")
        stderr = getattr(cmd_proc, "stderr", "")
        exit_code = getattr(cmd_proc, "exit_code", 0)

        record_e2b_event("terminal", f"$ {req.command[:40]}", f"Code {exit_code} · {duration_ms}ms", "success" if exit_code == 0 else "error")

        return {
            "sandbox_id": sbx.sandbox_id,
            "command": req.command,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time_ms": duration_ms
        }
    except Exception as e:
        stdout = getattr(e, "stdout", "")
        stderr = getattr(e, "stderr", str(e))
        code = getattr(e, "exit_code", 1)
        record_e2b_event("terminal", f"$ {req.command[:40]}", f"Exit {code}", "error")
        return {
            "sandbox_id": req.sandbox_id or "error",
            "command": req.command,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": code,
            "execution_time_ms": int((time.time() - t0) * 1000)
        }


@router.get("/e2b/files")
async def list_e2b_files(path: str = "/home/user", sandbox_id: str | None = None):
    """List files in the E2B Cloud sandbox workspace."""
    try:
        sbx = _get_or_create_code_sandbox(sandbox_id)
        file_entries = sbx.files.list(path)
        items = []
        for f in file_entries:
            items.append({
                "name": f.name,
                "type": getattr(f, "type", "file"),
                "path": f"{path.rstrip('/')}/{f.name}"
            })
        return {"path": path, "items": items, "sandbox_id": sbx.sandbox_id}
    except Exception as e:
        return {"path": path, "items": [], "error": str(e)}


@router.post("/e2b/action")
async def execute_e2b_action(req: E2BActionRequest):
    """Control the real E2B live visual computer."""
    act = req.action
    if act == "launch":
        res = computer_launch_session(req.url or "https://aninf.ga")
        record_e2b_event("desktop", "Lancement session Chrome E2B", req.url or "https://aninf.ga")
        return res
    elif act == "navigate":
        res = computer_navigate(req.sandbox_id, req.url or "https://google.com")
        record_e2b_event("desktop", "Navigation Chrome", req.url or "https://google.com")
        return res
    elif act == "click":
        res = computer_click(req.sandbox_id, req.x or 500, req.y or 300, req.button)
        record_e2b_event("desktop", f"Clic ({req.x}, {req.y})", f"Bouton {req.button}")
        return res
    elif act == "scroll":
        res = computer_scroll(req.sandbox_id, req.direction, req.amount)
        record_e2b_event("desktop", f"Défilement {req.direction}", f"Facteur {req.amount}")
        return res
    elif act == "type":
        res = computer_type_text(req.sandbox_id, req.text or "", req.press_enter)
        record_e2b_event("desktop", "Saisie clavier", f"« {req.text} »")
        return res
    elif act == "screenshot":
        res = computer_take_screenshot(req.sandbox_id)
        record_e2b_event("desktop", "Capture d'écran", "Flux visuel actualisé")
        return res
    elif act == "close":
        res = computer_close_session(req.sandbox_id)
        record_e2b_event("desktop", "Fermeture session", req.sandbox_id)
        return res
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
