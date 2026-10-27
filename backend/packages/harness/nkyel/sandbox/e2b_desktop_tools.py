"""E2B Desktop Live Visual Computer Toolset for Ñkyel Studio."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[5]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "backend/.env")

E2B_API_KEY = os.getenv("E2B_API_KEY")

ACTIVE_SESSIONS: dict[str, Any] = {}


def _get_api_key() -> str:
    key = os.getenv("E2B_API_KEY", E2B_API_KEY)
    if not key:
        raise ValueError("E2B_API_KEY is not set.")
    return key


def computer_launch_session(initial_url: str = "https://google.com") -> dict[str, Any]:
    """Create an E2B Desktop Sandbox, start Chrome, and open the initial URL."""
    from e2b_desktop import Sandbox

    api_key = _get_api_key()
    sandbox = Sandbox.create(api_key=api_key)
    ACTIVE_SESSIONS[sandbox.sandbox_id] = sandbox

    # Open initial URL in Chrome
    sandbox.open(initial_url)
    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    # Retrieve live stream URL if available
    stream_url = ""
    try:
        stream_url = sandbox.stream.get_url()
    except Exception:
        stream_url = f"https://{sandbox.sandbox_id}.{sandbox.sandbox_domain}"

    return {
        "sandbox_id": sandbox.sandbox_id,
        "current_url": initial_url,
        "stream_url": stream_url,
        "screenshot_base64": b64_img,
        "status": "RUNNING"
    }


def computer_navigate(sandbox_id: str, url: str) -> dict[str, Any]:
    """Navigate to a URL in the active Chrome instance."""
    sandbox = ACTIVE_SESSIONS.get(sandbox_id)
    if not sandbox:
        return {"error": f"Session {sandbox_id} not found."}

    sandbox.open(url)
    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "sandbox_id": sandbox_id,
        "current_url": url,
        "screenshot_base64": b64_img,
        "status": "NAVIGATED"
    }


def computer_click(sandbox_id: str, x: int, y: int, button: str = "left") -> dict[str, Any]:
    """Move to coordinates (x, y) and click."""
    sandbox = ACTIVE_SESSIONS.get(sandbox_id)
    if not sandbox:
        return {"error": f"Session {sandbox_id} not found."}

    sandbox.move_mouse(x, y)
    if button == "right":
        sandbox.right_click()
    elif button == "double":
        sandbox.double_click()
    else:
        sandbox.left_click()

    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "sandbox_id": sandbox_id,
        "action": f"click_{button}",
        "x": x,
        "y": y,
        "screenshot_base64": b64_img
    }


def computer_scroll(sandbox_id: str, direction: str = "down", amount: int = 3) -> dict[str, Any]:
    """Scroll mouse wheel in the browser."""
    sandbox = ACTIVE_SESSIONS.get(sandbox_id)
    if not sandbox:
        return {"error": f"Session {sandbox_id} not found."}

    scroll_amount = amount if direction == "down" else -amount
    sandbox.scroll(scroll_amount)

    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "sandbox_id": sandbox_id,
        "action": "scroll",
        "direction": direction,
        "screenshot_base64": b64_img
    }


def computer_type_text(sandbox_id: str, text: str, press_enter: bool = False) -> dict[str, Any]:
    """Type keyboard text into the focused field."""
    sandbox = ACTIVE_SESSIONS.get(sandbox_id)
    if not sandbox:
        return {"error": f"Session {sandbox_id} not found."}

    sandbox.write(text)
    if press_enter:
        sandbox.press("Enter")

    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "sandbox_id": sandbox_id,
        "action": "typed_text",
        "length": len(text),
        "screenshot_base64": b64_img
    }


def computer_take_screenshot(sandbox_id: str) -> dict[str, Any]:
    """Capture a fresh screenshot of the current screen."""
    sandbox = ACTIVE_SESSIONS.get(sandbox_id)
    if not sandbox:
        return {"error": f"Session {sandbox_id} not found."}

    screenshot_bytes = sandbox.screenshot()
    b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "sandbox_id": sandbox_id,
        "screenshot_base64": b64_img
    }


def computer_close_session(sandbox_id: str) -> dict[str, Any]:
    """Close and clean up the E2B desktop sandbox."""
    sandbox = ACTIVE_SESSIONS.pop(sandbox_id, None)
    if sandbox:
        try:
            sandbox.kill()
        except Exception:
            pass
        return {"sandbox_id": sandbox_id, "status": "TERMINATED"}
    return {"sandbox_id": sandbox_id, "status": "NOT_FOUND"}
