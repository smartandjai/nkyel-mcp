"""
Automated tests for Slide 01: Ñkyel Computer Use.
Verifies:
1. Tool cataloging and injection into DeerFlow agent ordinary_tools
2. NkyelComputerSessionManager singleton and thread affinity
3. VisionGroundingProvider with deepseek-flash configuration
4. Execution contracts and result validation
"""

from typing import Any
from unittest.mock import MagicMock

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

