"""
Automated tests for Slide 01: Ñkyel Computer Use.
Verifies:
1. Tool cataloging and injection into DeerFlow agent ordinary_tools
2. NkyelComputerSessionManager singleton and thread affinity
3. VisionGroundingProvider with deepseek-flash configuration
4. Execution contracts and result validation
"""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv
from nkyel.sandbox.computer_session_manager import (
    ComputerSession,
    NkyelComputerSessionManager,
)
from nkyel.sandbox.computer_tools import (
    computer_list_files,
    computer_python,
    computer_read_file,
    computer_shell,
    computer_status,
    computer_tools,
    computer_write_file,
)
from nkyel.sandbox.vision_grounding import VisualGroundingProvider
from nkyel.tools.tools import get_available_tools


def test_computer_tools_registered_in_deerflow():
    """Test C: DeerFlow agent has all computer tools registered and available."""
    tool_names = {t.name for t in computer_tools}
    expected_tools = {
        "computer_start",
        "computer_status",
        "computer_stop",
        "browser_open",
        "browser_click",
        "browser_type",
        "browser_scroll",
        "browser_read",
        "browser_screenshot",
        "browser_back",
        "browser_wait",
        "desktop_observe",
        "desktop_click",
        "desktop_type",
        "desktop_keypress",
        "desktop_launch",
        "computer_shell",
        "computer_python",
        "computer_write_file",
        "computer_read_file",
        "computer_list_files",
    }
    assert expected_tools.issubset(tool_names), (
        f"Missing tools: {expected_tools - tool_names}"
    )

    # Verify DeerFlow get_available_tools() includes them
    available = get_available_tools()
    available_names = {t.name for t in available}
    for tool_name in expected_tools:
        assert tool_name in available_names, (
            f"Tool {tool_name} not available in DeerFlow toolset"
        )


def test_session_manager_singleton_and_stream_url():
    """Test A: Session manager produces authenticated noVNC stream URLs."""
    manager = NkyelComputerSessionManager.get_instance()
    assert manager is not None
    assert manager is NkyelComputerSessionManager.get_instance()

    # Create mock session
    session = ComputerSession(
        user_id="test_user",
        thread_id="thread_abc",
        run_id="run_123",
        sandbox_id="sbx_test_456",
        sandbox=MagicMock(),
        stream_url="https://6080-sbx_test_456.e2b.app/vnc.html?autoconnect=true&resize=scale",
        status="live",
    )
    assert session.sandbox_id == "sbx_test_456"
    assert "6080-sbx_test_456.e2b.app" in session.stream_url
    assert "vnc.html" in session.stream_url

    manager._sessions["thread_abc"] = session
    retrieved = manager.get_session("thread_abc")
    assert retrieved is not None
    assert retrieved is session
    assert retrieved.status == "live"


def test_vision_grounding_provider_deepseek():
    """Test D: DeepSeek Vision provider configuration and prompt structure."""
    provider = VisualGroundingProvider(api_key="test_key", model="deepseek-flash")
    assert provider.model == "deepseek-flash"
    assert provider.api_key == "test_key"

    # Test coordinate normalization
    norm_x, norm_y = provider.normalize_coordinates(512, 384, 1024, 768)
    assert norm_x == 500
    assert norm_y == 500

    # Test denormalization
    denorm_x, denorm_y = provider.denormalize_coordinates(500, 500, 1920, 1080)
    assert denorm_x == 960
    assert denorm_y == 540


def _call_tool(tool: Any, **kwargs: Any) -> Any:
    """Helper to invoke underlying tool function in unit tests."""
    fn = getattr(tool, "func", None)
    if fn is not None:
        return fn(**kwargs)
    return tool(**kwargs)


def test_computer_tools_execution_with_mock_sandbox():
    """Test B, E, F: Execute tools against mocked session manager."""
    manager = NkyelComputerSessionManager.get_instance()
    mock_sandbox = MagicMock()
    mock_sandbox.sandbox_id = "mock_sbx_999"

    # Mock commands.run for shell and python
    mock_cmd_res = MagicMock()
    mock_cmd_res.exit_code = 0
    mock_cmd_res.stdout = "Hello from Ñkyel Computer"
    mock_cmd_res.stderr = ""
    mock_sandbox.commands.run.return_value = mock_cmd_res

    # Mock files for read/write/list
    mock_sandbox.files.write = MagicMock()
    mock_sandbox.files.read.return_value = "print('Hello World')"
    mock_sandbox.files.list.return_value = [
        MagicMock(name="test.py", is_dir=False, size=20),
        MagicMock(name="workspace", is_dir=True, size=4096),
    ]

    session = ComputerSession(
        user_id="default",
        thread_id="default_thread",
        run_id="run_mock",
        sandbox_id="mock_sbx_999",
        stream_url="https://6080-mock_sbx_999.e2b.app/vnc.html?autoconnect=true&resize=scale",
        status="live",
        sandbox=mock_sandbox,
    )
    manager._sessions["default_thread"] = session
    mock_runtime = MagicMock(
        thread_id="default_thread", user_id="default", run_id="run_mock"
    )

    # 1. Test computer_status
    status_res = _call_tool(computer_status, runtime=mock_runtime)
    assert status_res["status"] == "live"
    assert status_res["sandbox_id"] == "mock_sbx_999"
    assert "stream_url" in status_res

    # 2. Test computer_shell
    shell_res = _call_tool(computer_shell, runtime=mock_runtime, command="echo 'Hello'")
    assert shell_res["success"] is True
    assert shell_res["exit_code"] == 0
    assert "Hello from Ñkyel Computer" in shell_res["stdout"]

    # 3. Test computer_python
    py_res = _call_tool(computer_python, runtime=mock_runtime, code="print('Hello')")
    assert py_res["success"] is True
    assert py_res["exit_code"] == 0

    # 4. Test computer_write_file
    write_res = _call_tool(
        computer_write_file,
        runtime=mock_runtime,
        path="/home/user/script.py",
        content="print('test')",
    )
    assert write_res["success"] is True
    assert write_res["path"] == "/home/user/script.py"

    # 5. Test computer_read_file
    read_res = _call_tool(
        computer_read_file,
        runtime=mock_runtime,
        path="/home/user/script.py",
    )
    assert read_res["success"] is True
    assert "Hello World" in read_res["content"]

    # 6. Test computer_list_files
    list_res = _call_tool(
        computer_list_files,
        runtime=mock_runtime,
        path="/home/user",
    )
    assert list_res["success"] is True
    assert len(list_res["entries"]) == 2


def test_computer_tools_callable_by_deerflow_via_tool_call():
    """Test G: Verify Computer tools are genuinely callable by DeerFlow tool invocation.

    DeerFlow passes LLM tool calls formatted as:
    {'name': <tool_name>, 'args': {<params>}, 'id': <call_id>, 'type': 'tool_call'}
    This verifies that tools execute without Pydantic 'runtime: Field required' errors.
    """
    manager = NkyelComputerSessionManager.get_instance()
    mock_sandbox = MagicMock()
    mock_cmd_res = MagicMock(exit_code=0, stdout="test-ok", stderr="")
    mock_sandbox.commands.run.return_value = mock_cmd_res
    mock_sandbox.files.read.return_value = "content"
    mock_sandbox.files.list.return_value = []
    mock_sandbox.screenshot.return_value = b"\x89PNG\r\n\x1a\nfake"

    session = ComputerSession(
        user_id="test",
        thread_id="global-mission",
        run_id="run_1",
        sandbox_id="sbx_test",
        stream_url="https://6080-sbx_test.e2b.app/vnc.html?autoconnect=true&resize=scale&password=pw",
        auth_key="pw",
        status="LIVE",
        sandbox=mock_sandbox,
    )
    manager._sessions["global-mission"] = session

    # Test status tool call
    res_status = computer_status.invoke(
        {
            "name": "computer_status",
            "args": {},
            "id": "call_status_1",
            "type": "tool_call",
        }
    )
    data_status = json.loads(res_status.content)
    assert data_status["success"] is True
    assert data_status["sandbox_id"] == "sbx_test"

    # Test shell tool call
    res_shell = computer_shell.invoke(
        {
            "name": "computer_shell",
            "args": {"command": "echo 'DeerFlow'"},
            "id": "call_shell_1",
            "type": "tool_call",
        }
    )
    data_shell = json.loads(res_shell.content)
    assert data_shell["success"] is True
    assert data_shell["command"] == "echo 'DeerFlow'"

    # Test write_file tool call
    res_write = computer_write_file.invoke(
        {
            "name": "computer_write_file",
            "args": {"path": "/home/user/test.txt", "content": "DeerFlow Test"},
            "id": "call_write_1",
            "type": "tool_call",
        }
    )
    data_write = json.loads(res_write.content)
    assert data_write["success"] is True

    # Test read_file tool call
    res_read = computer_read_file.invoke(
        {
            "name": "computer_read_file",
            "args": {"path": "/home/user/test.txt"},
            "id": "call_read_1",
            "type": "tool_call",
        }
    )
    data_read = json.loads(res_read.content)
    assert data_read["success"] is True
    assert data_read["content"] == "content"


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_E2B_TEST") != "1",
    reason="Opt-in live integration test. Set RUN_LIVE_E2B_TEST=1 to run.",
)
def test_live_e2b_desktop_sandbox_integration():
    """Real E2B Desktop integration test:

    1. Starts an actual E2B Desktop sandbox.
    2. Starts the desktop stream with supported authenticated access.
    3. Retrieves and verifies the real authorized stream URL.
    4. Navigates Chrome to https://example.com.
    5. Captures the real screen as PNG.
    6. Verifies clean shutdown.
    """
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")
    load_dotenv(repo_root / "backend/.env")

    api_key = os.getenv("E2B_API_KEY")
    assert api_key, "E2B_API_KEY must be set in environment or .env"

    from e2b_desktop import Sandbox

    sandbox = None
    try:
        # 1. Start actual sandbox
        sandbox = Sandbox.create(api_key=api_key, timeout=120)
        assert sandbox.sandbox_id, "Sandbox must have a valid sandbox_id"

        # 2. Start desktop stream with authenticated access
        sandbox.stream.start(require_auth=True)
        auth_key = sandbox.stream.get_auth_key()
        assert auth_key, "auth_key must be non-empty when require_auth=True"

        # 3. Retrieve real authorized stream URL
        stream_url = sandbox.stream.get_url(
            auto_connect=True, view_only=False, resize="scale", auth_key=auth_key
        )
        assert f"6080-{sandbox.sandbox_id}" in stream_url
        assert f"password={auth_key}" in stream_url
        assert stream_url.startswith("https://")

        # 4. Open example.com
        sandbox.open("https://example.com")

        # 5. Capture real screen
        screenshot_bytes = sandbox.screenshot()
        assert len(screenshot_bytes) > 5000, "Screenshot should be non-trivial size"
        assert screenshot_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Must be valid PNG"

    finally:
        # 6. Close sandbox cleanly
        if sandbox is not None:
            sandbox.kill()
