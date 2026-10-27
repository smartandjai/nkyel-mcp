"""Nkyel Computer Session Manager — Unified E2B Desktop Sandbox Lifecycle.

Manages one single cloud graphical computer (E2B Desktop Sandbox) per active mission.
The same sandbox is preserved and shared across Browser, Terminal, Python, Code files,
Screenshots, Filesystem, and live Desktop streaming (noVNC).
"""

from __future__ import annotations

import base64
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[5]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "backend/.env")

logger = logging.getLogger(__name__)

# Fallback default timeout: 10 minutes (600s)
DEFAULT_SANDBOX_TIMEOUT_SEC = 600


@dataclass
class ComputerSession:
    user_id: str
    thread_id: str
    run_id: str
    sandbox_id: str
    sandbox: Any  # e2b_desktop.Sandbox
    provider: str = "e2b_desktop"
    status: str = "STARTING"  # STARTING, LIVE, AGENT_CONTROLLING, USER_CONTROLLING, PAUSED, CLOSED, FAILED
    stream_url: str = ""
    current_url: str = ""
    page_title: str = ""
    current_app: str = "Desktop"
    created_at: float = field(default_factory=time.time)
    last_activity_at: float = field(default_factory=time.time)
    current_tool_call_id: str | None = None
    last_screenshot_b64: str | None = None
    terminal_logs: list[dict[str, Any]] = field(default_factory=list)
    action_events: list[dict[str, Any]] = field(default_factory=list)

    def touch(self) -> None:
        self.last_activity_at = time.time()

    def add_event(self, event_type: str, action: str, details: str, status: str = "success") -> dict[str, Any]:
        evt = {"id": f"evt-{int(time.time() * 1000)}", "type": event_type, "action": action, "details": details, "status": status, "timestamp": datetime.now(UTC).strftime("%H:%M:%S")}
        self.action_events.append(evt)
        if len(self.action_events) > 80:
            del self.action_events[:-60]
        self.touch()
        return evt

    def add_terminal_log(self, command: str, stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
        log_entry = {"id": f"term-{int(time.time() * 1000)}", "command": command, "stdout": stdout, "stderr": stderr, "exit_code": exit_code, "timestamp": datetime.now(UTC).strftime("%H:%M:%S")}
        self.terminal_logs.append(log_entry)
        if len(self.terminal_logs) > 60:
            del self.terminal_logs[:-40]
        self.touch()
        return log_entry


class NkyelComputerSessionManager:
    """Singleton session manager maintaining thread-bound E2B Desktop sessions."""

    _instance: NkyelComputerSessionManager | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._sessions: dict[str, ComputerSession] = {}  # thread_id -> ComputerSession
        self._sandbox_map: dict[str, str] = {}  # sandbox_id -> thread_id

    @classmethod
    def get_instance(cls) -> NkyelComputerSessionManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _get_api_key(self) -> str:
        key = os.getenv("E2B_API_KEY")
        if not key:
            raise ValueError("E2B_API_KEY is not configured in environment.")
        return key

    def get_session(self, thread_id: str) -> ComputerSession | None:
        return self._sessions.get(thread_id)

    def get_by_sandbox_id(self, sandbox_id: str) -> ComputerSession | None:
        thread_id = self._sandbox_map.get(sandbox_id)
        if thread_id:
            return self._sessions.get(thread_id)
        return None

    def get_or_create_session(
        self,
        thread_id: str,
        user_id: str = "default",
        run_id: str = "",
        initial_url: str = "https://example.com",
        timeout: int = DEFAULT_SANDBOX_TIMEOUT_SEC,
    ) -> ComputerSession:
        """Get the active desktop session for the thread or initialize a new one."""
        with self._lock:
            existing = self._sessions.get(thread_id)
            if existing:
                try:
                    if getattr(existing.sandbox, "is_running", lambda: True)():
                        existing.touch()
                        return existing
                except Exception:
                    logger.warning(f"Existing session for thread {thread_id} dead, recreating...")

            logger.info(f"Initializing new E2B Desktop sandbox for thread={thread_id}, user={user_id}")
            from e2b_desktop import Sandbox

            api_key = self._get_api_key()
            sandbox = Sandbox.create(api_key=api_key, timeout=timeout)
            sandbox_id = sandbox.sandbox_id

            # Start VNC stream immediately so the authenticated live URL is available
            stream_url = ""
            try:
                sandbox.stream.start()
                stream_url = sandbox.stream.get_url(auto_connect=True, view_only=False, resize="scale")
                logger.info(f"VNC Stream started for sandbox {sandbox_id}: {stream_url}")
            except Exception as stream_err:
                logger.warning(f"Could not start VNC stream: {stream_err}")
                stream_url = f"https://{sandbox_id}.{getattr(sandbox, 'sandbox_domain', 'e2b.app')}"

            session = ComputerSession(
                user_id=user_id,
                thread_id=thread_id,
                run_id=run_id,
                sandbox_id=sandbox_id,
                sandbox=sandbox,
                status="LIVE",
                stream_url=stream_url,
                current_url=initial_url,
                current_app="Chrome Browser",
            )
            session.add_event("lifecycle", "computer_start", f"E2B Cloud Computer initialized ({sandbox_id})")

            # Launch visible Chrome on DISPLAY=:0 with the initial URL
            try:
                # Open initial URL via xdg-open on display :0
                sandbox.open(initial_url)
                session.add_event("browser", "browser_open", f"Opened Chrome with {initial_url}")
            except Exception as launch_err:
                logger.warning(f"Initial browser launch: {launch_err}")

            # Capture initial screenshot
            try:
                shot = sandbox.screenshot()
                session.last_screenshot_b64 = base64.b64encode(shot).decode("utf-8")
            except Exception:
                pass

            self._sessions[thread_id] = session
            self._sandbox_map[sandbox_id] = thread_id
            return session

    def close_session(self, thread_id: str) -> bool:
        """Clean up and terminate the sandbox for the thread."""
        with self._lock:
            session = self._sessions.pop(thread_id, None)
            if not session:
                return False
            self._sandbox_map.pop(session.sandbox_id, None)
            session.status = "CLOSED"
            try:
                session.sandbox.kill()
                logger.info(f"Killed sandbox {session.sandbox_id} for thread {thread_id}")
            except Exception as e:
                logger.warning(f"Error terminating sandbox {session.sandbox_id}: {e}")
            return True


# Global singleton helper
computer_sessions = NkyelComputerSessionManager.get_instance()
