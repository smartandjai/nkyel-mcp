"""Ñkyel Autonomous Computer Toolkit for DeerFlow Agent.

Exposes complete cloud computer capabilities (E2B Desktop Sandbox):
- Lifecycle: computer_start, computer_status, computer_stop
- Browser: browser_open, browser_click, browser_type, browser_scroll, browser_read, browser_screenshot, browser_tabs, browser_back, browser_wait
- Desktop: desktop_observe, desktop_click, desktop_move, desktop_type, desktop_keypress, desktop_scroll, desktop_launch
- Terminal & Code: computer_shell, computer_python, computer_write_file, computer_read_file, computer_list_files, computer_download_file
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Annotated, Any

from langchain.tools import InjectedToolCallId, tool

from nkyel.sandbox.computer_session_manager import ComputerSession, computer_sessions
from nkyel.sandbox.vision_grounding import visual_grounding
from nkyel.tools.types import Runtime

logger = logging.getLogger(__name__)


def _resolve_session(runtime: Runtime | None, thread_id: str | None = None) -> ComputerSession:
    """Helper to resolve active session from runtime or fallback."""
    tid = thread_id or getattr(runtime, "thread_id", None) or "global-mission"
    user_id = getattr(runtime, "user_id", None) or "default"
    run_id = getattr(runtime, "run_id", None) or ""
    return computer_sessions.get_or_create_session(thread_id=tid, user_id=user_id, run_id=run_id)


def _format_result(action: str, success: bool, session: ComputerSession, tool_call_id: str = "", duration: float = 0.0, **kwargs: Any) -> dict[str, Any]:
    """Uniform structured tool output contract."""
    res = {
        "tool_call_id": tool_call_id,
        "run_id": session.run_id,
        "sandbox_id": session.sandbox_id,
        "action": action,
        "success": success,
        "status": session.status,
        "current_url": session.current_url,
        "page_title": session.page_title,
        "current_app": session.current_app,
        "stream_url": session.stream_url,
        "auth_key": getattr(session, "auth_key", ""),
        "duration_sec": round(duration, 3),
        **kwargs,
    }
    return res


# ─── Lifecycle Tools ─────────────────────────────────────────────────────────


@tool("computer_start")
def computer_start_tool(initial_url: str = "https://example.com", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Start or attach to the active Ñkyel Cloud Computer (E2B Desktop).

    Use this when beginning a mission requiring a live graphical computer,
    visible browser navigation, code execution, or file inspection.

    Args:
        initial_url: The starting web URL to open in Chrome on the live desktop.
    """
    t0 = time.time()
    try:
        session = _resolve_session(runtime)
        if initial_url and initial_url != session.current_url:
            session.sandbox.open(initial_url)
            session.current_url = initial_url
            session.add_event("browser", "open", f"Navigated to {initial_url}")

        shot = session.sandbox.screenshot()
        b64 = base64.b64encode(shot).decode("utf-8")
        session.last_screenshot_b64 = b64

        return _format_result("computer_start", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, observation=f"Computer is live ({session.sandbox_id}). Live stream URL: {session.stream_url}", screenshot_base64=b64)
    except Exception as e:
        logger.error(f"computer_start failed: {e}")
        return {"action": "computer_start", "success": False, "error": str(e)}


@tool("computer_status")
def computer_status_tool(runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Check the health, current URL, active application and stream URL of the computer."""
    t0 = time.time()
    session = _resolve_session(runtime)
    return _format_result("computer_status", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, observation=f"Status: {session.status}, App: {session.current_app}, URL: {session.current_url}")


@tool("computer_stop")
def computer_stop_tool(runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Close and terminate the cloud computer when the mission is completed."""
    t0 = time.time()
    tid = getattr(runtime, "thread_id", None) or "global-mission"
    session = computer_sessions.get_session(tid)
    if session:
        computer_sessions.close_session(tid)
        return {"action": "computer_stop", "success": True, "sandbox_id": session.sandbox_id, "status": "CLOSED", "duration_sec": round(time.time() - t0, 3)}
    return {"action": "computer_stop", "success": True, "status": "NO_ACTIVE_SESSION", "duration_sec": round(time.time() - t0, 3)}


# ─── Browser Tools ──────────────────────────────────────────────────────────


@tool("browser_open")
def browser_open_tool(url: str, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Navigate visible Google Chrome to a web URL inside the cloud computer.

    The user watches Chrome visibly load the webpage on the live desktop stream.

    Args:
        url: Complete HTTP or HTTPS website URL to visit.
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.open(url)
    session.current_url = url
    session.current_app = "Google Chrome"
    session.add_event("browser", "navigate", f"Visited {url}")

    time.sleep(2)  # Give Chrome time to render
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64

    # Extract page title and text via dom query
    title = url
    text_sample = ""
    try:
        res = session.sandbox.commands.run(f"DISPLAY=:0 google-chrome-stable --no-sandbox --headless=new --dump-dom '{url}' 2>/dev/null | head -n 30", timeout=10)
        text_sample = res.stdout.strip()[:400]
    except Exception:
        pass

    return _format_result("browser_open", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, observation=f"Successfully navigated Chrome to {url}.", page_title=title, text_sample=text_sample, screenshot_base64=b64)


@tool("browser_click")
def browser_click_tool(x: int | None = None, y: int | None = None, button: str = "left", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Click on the web page at screen coordinates (x, y).

    Args:
        x: Horizontal coordinate in pixels (0-1024).
        y: Vertical coordinate in pixels (0-768).
        button: Mouse button ('left', 'right', or 'double').
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    click_x = x if x is not None else 512
    click_y = y if y is not None else 384

    session.sandbox.move_mouse(click_x, click_y)
    if button == "right":
        session.sandbox.right_click()
    elif button == "double":
        session.sandbox.double_click()
    else:
        session.sandbox.left_click()

    session.add_event("browser", f"click_{button}", f"Clicked at ({click_x}, {click_y})")
    time.sleep(1)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64

    return _format_result("browser_click", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, x=click_x, y=click_y, button=button, observation=f"Clicked at coordinates ({click_x}, {click_y}).", screenshot_base64=b64)


@tool("browser_type")
def browser_type_tool(text: str, press_enter: bool = False, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Type keyboard text into the focused browser input field.

    Args:
        text: The string to type.
        press_enter: Whether to press Enter after typing.
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.write(text)
    if press_enter:
        session.sandbox.press("Enter")

    session.add_event("browser", "type", f"Typed {len(text)} characters" + (" and Enter" if press_enter else ""))
    time.sleep(1)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64

    return _format_result("browser_type", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, text_length=len(text), press_enter=press_enter, observation=f"Typed text: {text[:50]}...", screenshot_base64=b64)


@tool("browser_scroll")
def browser_scroll_tool(direction: str = "down", amount: int = 3, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Scroll the active web page up or down.

    Args:
        direction: 'down' or 'up'.
        amount: Number of scroll units (default 3).
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    delta = amount if direction == "down" else -amount
    session.sandbox.scroll(delta)
    session.add_event("browser", "scroll", f"Scrolled {direction} by {amount}")

    time.sleep(1)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64

    return _format_result("browser_scroll", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, direction=direction, amount=amount, observation=f"Scrolled {direction} {amount} ticks.", screenshot_base64=b64)


@tool("browser_read")
def browser_read_tool(runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Read visible content, text, and active URL from the current browser session."""
    t0 = time.time()
    session = _resolve_session(runtime)
    content = ""
    try:
        res = session.sandbox.commands.run(f"DISPLAY=:0 google-chrome-stable --no-sandbox --headless=new --dump-dom '{session.current_url}' 2>/dev/null", timeout=15)
        content = res.stdout.strip()
    except Exception as e:
        content = f"Snapshot read error: {e}"

    return _format_result("browser_read", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, url=session.current_url, content=content[:1500], observation=f"Read content from {session.current_url} ({len(content)} chars).")


@tool("browser_screenshot")
def browser_screenshot_tool(runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Capture an instant high-resolution screenshot of the browser desktop."""
    t0 = time.time()
    session = _resolve_session(runtime)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64
    return _format_result("browser_screenshot", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, screenshot_base64=b64, observation="Captured fresh screenshot of cloud desktop.")


@tool("browser_back")
def browser_back_tool(runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Navigate backward in browser history using Alt+Left."""
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.press("Alt+Left")
    session.add_event("browser", "back", "Navigated back")
    time.sleep(1)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    return _format_result("browser_back", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, screenshot_base64=b64)


@tool("browser_wait")
def browser_wait_tool(seconds: int = 2, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Wait for page elements or async content to finish loading."""
    t0 = time.time()
    session = _resolve_session(runtime)
    wait_time = min(max(seconds, 1), 10)
    time.sleep(wait_time)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    return _format_result("browser_wait", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, observation=f"Waited {wait_time}s for page to settle.", screenshot_base64=b64)


# ─── Desktop Graphical Tools ────────────────────────────────────────────────


@tool("desktop_observe")
def desktop_observe_tool(instruction: str = "Analyze screen and recommend next action", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Capture screen and invoke DeepSeek Vision model to analyze visible elements.

    Args:
        instruction: What visual goal to inspect or verify on screen.
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    session.last_screenshot_b64 = b64

    # Run vision analysis
    vision_res = visual_grounding.analyze_screen(screenshot_b64=b64, screen_width=1024, screen_height=768, instruction=instruction)

    return _format_result(
        "desktop_observe", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, vision_analysis=vision_res, screenshot_base64=b64, observation=vision_res.get("observation") or "Screen observed and analyzed."
    )


@tool("desktop_click")
def desktop_click_tool(x: int, y: int, button: str = "left", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Move cursor to coordinate (x, y) on the graphical desktop and click."""
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.move_mouse(x, y)
    if button == "right":
        session.sandbox.right_click()
    elif button == "double":
        session.sandbox.double_click()
    else:
        session.sandbox.left_click()

    session.add_event("desktop", f"click_{button}", f"Mouse click at ({x}, {y})")
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    return _format_result("desktop_click", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, x=x, y=y, button=button, screenshot_base64=b64)


@tool("desktop_type")
def desktop_type_tool(text: str, press_enter: bool = False, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Type text into active desktop window."""
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.write(text)
    if press_enter:
        session.sandbox.press("Enter")
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    return _format_result("desktop_type", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, screenshot_base64=b64)


@tool("desktop_keypress")
def desktop_keypress_tool(key: str, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Press keyboard key or key combination (e.g. 'Enter', 'Escape', 'ctrl+c')."""
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.press(key)
    session.add_event("desktop", "keypress", f"Pressed key {key}")
    return _format_result("desktop_keypress", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, key=key)


@tool("desktop_launch")
def desktop_launch_tool(app_name: str, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Launch an application on the graphical desktop (e.g. 'google-chrome', 'xfce4-terminal')."""
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.launch(app_name)
    session.current_app = app_name
    session.add_event("desktop", "launch", f"Launched application {app_name}")
    time.sleep(2)
    shot = session.sandbox.screenshot()
    b64 = base64.b64encode(shot).decode("utf-8")
    return _format_result("desktop_launch", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, app_name=app_name, screenshot_base64=b64)


# ─── Terminal, Python & Filesystem Tools (SAME MACHINE!) ─────────────────────


@tool("computer_shell")
def computer_shell_tool(command: str, workdir: str | None = None, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Execute a bash shell command inside the SAME cloud computer sandbox.

    All outputs, environment changes, and files reside on the same machine the user watches.

    Args:
        command: Exact shell command line to run.
        workdir: Working directory (defaults to /home/user).
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    run_cmd = f"cd {workdir} && {command}" if workdir else command

    try:
        res = session.sandbox.commands.run(run_cmd, timeout=90)
        stdout = res.stdout
        stderr = res.stderr
        exit_code = 0
    except Exception as e:
        stdout = getattr(e, "stdout", "")
        stderr = getattr(e, "stderr", str(e))
        exit_code = getattr(e, "exit_code", 1)

    session.add_terminal_log(command, stdout, stderr, exit_code)
    session.add_event("terminal", "shell", f"Ran `{command[:40]}` (exit {exit_code})", status="success" if exit_code == 0 else "error")

    return _format_result(
        "computer_shell", exit_code == 0, session, tool_call_id=tool_call_id, duration=time.time() - t0, command=command, stdout=stdout, stderr=stderr, exit_code=exit_code, observation=f"Command finished with exit code {exit_code}."
    )


@tool("computer_python")
def computer_python_tool(code: str, filename: str = "script.py", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Write and execute Python code in the active cloud computer sandbox.

    Saves the script to /home/user/{filename} and executes it with Python 3.
    Output is captured and displayed in the terminal and code tabs.

    Args:
        code: Full Python code string to execute.
        filename: Target filename in /home/user/ (e.g. 'analyze_page.py').
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    filepath = f"/home/user/{filename}"

    # Write code file
    session.sandbox.files.write(filepath, code)
    session.add_event("code", "write", f"Saved Python script {filepath}")

    # Run script
    try:
        res = session.sandbox.commands.run(f"python3 {filepath}", timeout=90)
        stdout = res.stdout
        stderr = res.stderr
        exit_code = 0
    except Exception as e:
        stdout = getattr(e, "stdout", "")
        stderr = getattr(e, "stderr", str(e))
        exit_code = getattr(e, "exit_code", 1)

    session.add_terminal_log(f"python3 {filepath}", stdout, stderr, exit_code)
    session.add_event("code", "execute", f"Executed {filepath} (exit {exit_code})", status="success" if exit_code == 0 else "error")

    return _format_result(
        "computer_python", exit_code == 0, session, tool_call_id=tool_call_id, duration=time.time() - t0, filepath=filepath, stdout=stdout, stderr=stderr, exit_code=exit_code, observation=f"Executed {filename}:\nSTDOUT:\n{stdout[:1000]}"
    )


@tool("computer_write_file")
def computer_write_file_tool(path: str, content: str, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Write text data to a file inside the cloud computer.

    Args:
        path: Path inside sandbox (e.g. '/home/user/result.txt').
        content: Text content to write.
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    session.sandbox.files.write(path, content)
    session.add_event("filesystem", "write_file", f"Created file {path} ({len(content)} bytes)")
    return _format_result("computer_write_file", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, path=path, bytes_written=len(content), observation=f"File successfully created at {path}.")


@tool("computer_read_file")
def computer_read_file_tool(path: str, runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """Read file content from the cloud computer filesystem.

    Args:
        path: Absolute or relative file path to read.
    """
    t0 = time.time()
    session = _resolve_session(runtime)
    try:
        content = session.sandbox.files.read(path)
        return _format_result("computer_read_file", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, path=path, content=content, observation=f"Read {path} ({len(content)} chars):\n{content[:500]}")
    except Exception as e:
        return _format_result("computer_read_file", False, session, tool_call_id=tool_call_id, duration=time.time() - t0, path=path, error=str(e), observation=f"Could not read {path}: {e}")


@tool("computer_list_files")
def computer_list_files_tool(path: str = "/home/user", runtime: Runtime | None = None, tool_call_id: Annotated[str, InjectedToolCallId] = "") -> dict[str, Any]:
    """List directory contents and files in the cloud computer."""
    t0 = time.time()
    session = _resolve_session(runtime)
    try:
        entries = session.sandbox.files.list(path)
        formatted = [{"name": e.name, "type": getattr(e, "type", "file")} for e in entries]
        return _format_result(
            "computer_list_files", True, session, tool_call_id=tool_call_id, duration=time.time() - t0, path=path, entries=formatted, observation=f"Found {len(formatted)} entries in {path}: {[f['name'] for f in formatted]}"
        )
    except Exception as e:
        return _format_result("computer_list_files", False, session, tool_call_id=tool_call_id, duration=time.time() - t0, path=path, error=str(e))


# List of all autonomous computer tools for DeerFlow agent builder
ALL_COMPUTER_TOOLS = [
    computer_start_tool,
    computer_status_tool,
    computer_stop_tool,
    browser_open_tool,
    browser_click_tool,
    browser_type_tool,
    browser_scroll_tool,
    browser_read_tool,
    browser_screenshot_tool,
    browser_back_tool,
    browser_wait_tool,
    desktop_observe_tool,
    desktop_click_tool,
    desktop_type_tool,
    desktop_keypress_tool,
    desktop_launch_tool,
    computer_shell_tool,
    computer_python_tool,
    computer_write_file_tool,
    computer_read_file_tool,
    computer_list_files_tool,
]

computer_tools = ALL_COMPUTER_TOOLS
computer_start = computer_start_tool
computer_status = computer_status_tool
computer_stop = computer_stop_tool
browser_open = browser_open_tool
browser_click = browser_click_tool
browser_type = browser_type_tool
browser_scroll = browser_scroll_tool
browser_read = browser_read_tool
browser_screenshot = browser_screenshot_tool
browser_back = browser_back_tool
browser_wait = browser_wait_tool
desktop_observe = desktop_observe_tool
desktop_click = desktop_click_tool
desktop_type = desktop_type_tool
desktop_keypress = desktop_keypress_tool
desktop_launch = desktop_launch_tool
computer_shell = computer_shell_tool
computer_python = computer_python_tool
computer_write_file = computer_write_file_tool
computer_read_file = computer_read_file_tool
computer_list_files = computer_list_files_tool
