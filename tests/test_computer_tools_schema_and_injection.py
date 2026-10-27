"""Mandatory Regression Test Suite for Ñkyel Computer Tools JSON Schemas & Runtime Injection.

Verifies:
1. Exactly the 21 unique registered tools from ALL_COMPUTER_TOOLS.
2. convert_to_openai_tool(tool) succeeds for all 21 tools with NO PydanticInvalidForJsonSchema.
3. json.dumps() succeeds for all 21 tools.
4. Model-facing parameters are valid, and internal fields ('runtime', 'tool_call_id') are excluded.
5. Real LangGraph / DeerFlow runtime injection via ToolNode and StateGraph.
6. Real thread_id and user_id propagation with no 'global-mission' fallback.
7. Strict non-leakage of stream_url, auth_key, or base64 screenshots into LLM-visible tool outputs.
8. Validation of every tool in the full Ñkyel toolset (including Tavily and Composio).
"""

from __future__ import annotations

import json
from typing import Annotated
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from nkyel.sandbox.computer_session_manager import ComputerSession, computer_sessions
from nkyel.sandbox.computer_tools import (
    ALL_COMPUTER_TOOLS,
    browser_open_tool,
    browser_screenshot_tool,
    computer_start_tool,
    computer_status_tool,
    computer_stop_tool,
)
from nkyel.tools.tools import get_available_tools
from typing_extensions import TypedDict


def test_unique_computer_tools_count():
    """Test exactly the 21 unique registered tools from ALL_COMPUTER_TOOLS."""
    assert len(ALL_COMPUTER_TOOLS) == 21
    tool_names = [t.name for t in ALL_COMPUTER_TOOLS]
    assert len(set(tool_names)) == 21, f"Duplicate tool names found: {tool_names}"


@pytest.mark.parametrize(
    "tool", ALL_COMPUTER_TOOLS, ids=[t.name for t in ALL_COMPUTER_TOOLS]
)
def test_each_computer_tool_openai_schema_and_json_serialization(tool):
    """For each tool: convert_to_openai_tool, json.dumps, and assert clean parameters."""
    schema = convert_to_openai_tool(tool)
    assert isinstance(schema, dict)
    assert schema.get("type") == "function"
    assert "function" in schema
    assert schema["function"]["name"] == tool.name

    # JSON serialization must succeed without PydanticInvalidForJsonSchema or TypeError
    serialized = json.dumps(schema)
    assert serialized

    params = schema["function"]["parameters"]
    props = params.get("properties", {})

    # Injected fields must NEVER be exposed to the LLM
    assert "runtime" not in props, f"Tool '{tool.name}' exposed 'runtime' in parameters"
    assert "tool_call_id" not in props, (
        f"Tool '{tool.name}' exposed 'tool_call_id' in parameters"
    )


@pytest.mark.anyio
async def test_deerflow_toolnode_real_runtime_injection():
    """Verify that the actual DeerFlow tool executor (ToolNode) injects ToolRuntime cleanly."""

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], lambda a, b: a + b]

    # Setup mocked sandbox
    mock_sandbox = MagicMock()
    mock_sandbox.commands.run.return_value = MagicMock(
        exit_code=0, stdout="test-output", stderr=""
    )
    mock_sandbox.screenshot.return_value = b"\x89PNG\r\n\x1a\nfake-screenshot-data"
    mock_sandbox.open.return_value = None

    test_thread = "test_thread_real_injection"
    test_user = "user_clerk_verified_888"

    session = ComputerSession(
        user_id=test_user,
        thread_id=test_thread,
        run_id="run_test_01",
        sandbox_id="sbx_test_node_42",
        stream_url="https://6080-sbx_test_node_42.e2b.app/vnc.html?autoconnect=true&resize=scale&password=supersecret",
        auth_key="supersecret",
        status="LIVE",
        sandbox=mock_sandbox,
    )
    computer_sessions._sessions[test_thread] = session

    # Compile a real StateGraph with ToolNode containing computer tools
    node = ToolNode(
        [
            computer_start_tool,
            browser_open_tool,
            computer_status_tool,
            browser_screenshot_tool,
            computer_stop_tool,
        ]
    )
    builder = StateGraph(AgentState, context_schema=dict)
    builder.add_node("tools", node)
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    graph = builder.compile()

    # Invoke with LangGraph ToolCalls
    result = await graph.ainvoke(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "computer_start",
                            "args": {"initial_url": "https://example.com"},
                            "id": "call_start_01",
                            "type": "tool_call",
                        },
                        {
                            "name": "browser_open",
                            "args": {"url": "https://example.com/docs"},
                            "id": "call_open_02",
                            "type": "tool_call",
                        },
                        {
                            "name": "computer_status",
                            "args": {},
                            "id": "call_status_03",
                            "type": "tool_call",
                        },
                        {
                            "name": "browser_screenshot",
                            "args": {},
                            "id": "call_shot_04",
                            "type": "tool_call",
                        },
                    ],
                )
            ]
        },
        context={"thread_id": test_thread, "user_id": test_user},
    )

    # Validate ToolMessage results
    tool_messages = [m for m in result["messages"] if hasattr(m, "tool_call_id")]
    assert len(tool_messages) == 4

    for tm in tool_messages:
        content = json.loads(tm.content)
        assert content["success"] is True
        # STRICT CONTRACT: stream_url, auth_key, and base64 screenshot must NEVER leak to the LLM
        assert "stream_url" not in content, f"Leaked stream_url in {tm.tool_call_id}"
        assert "auth_key" not in content, f"Leaked auth_key in {tm.tool_call_id}"
        assert "screenshot_base64" not in content, (
            f"Leaked screenshot_base64 in {tm.tool_call_id}"
        )
        if "observation" in content:
            assert "supersecret" not in content["observation"]
            assert "vnc.html" not in content["observation"]

    # Verify session retained live data for frontend viewer
    active_session = computer_sessions.get_session(test_thread)
    assert active_session is not None
    assert "supersecret" in active_session.stream_url
    assert active_session.last_screenshot_b64 != ""


def test_no_global_mission_fallback():
    """Verify that omitting conversation thread_id raises ValueError rather than falling back to global-mission."""
    from langchain.tools import ToolRuntime
    from nkyel.sandbox.computer_tools import _resolve_session

    rt_empty = ToolRuntime(
        state={},
        context={},
        config={},
        stream_writer=lambda _: None,
        tools=[],
        tool_call_id="call-err",
        store=None,
    )
    with pytest.raises(ValueError) as exc:
        _resolve_session(rt_empty)
    assert "Cannot resolve active conversation thread_id" in str(exc.value)


def test_full_nkyel_toolset_schema_validation():
    """Validate every tool in the full Ñkyel model tool set (including Tavily and Composio)."""
    tools = get_available_tools()
    assert len(tools) > 0, "No tools returned by get_available_tools()"

    for tool in tools:
        schema = convert_to_openai_tool(tool)
        serialized = json.dumps(schema)
        assert serialized
        props = schema["function"]["parameters"].get("properties", {})
        assert "runtime" not in props, f"Tool '{tool.name}' exposed 'runtime'"
        assert "tool_call_id" not in props, f"Tool '{tool.name}' exposed 'tool_call_id'"
