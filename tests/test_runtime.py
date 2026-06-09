from autogenesis_agent.resources import ResourceRegistry
from autogenesis_agent.runtime import AgentRuntime
from autogenesis_agent.sessions import SessionManager
from autogenesis_agent.storage import connect
from autogenesis_agent.tools import PermissionLevel, ToolRegistry, echo_tool
from autogenesis_agent.tracing import TraceStore


def test_tool_registry_exposes_permission_metadata_and_executes_echo():
    registry = ToolRegistry()
    registry.register("echo", echo_tool, permission=PermissionLevel.READ_ONLY, description="Echo input")

    tool = registry.get("echo")
    result = registry.execute("echo", {"text": "hello"})

    assert tool.permission == PermissionLevel.READ_ONLY
    assert result == {"text": "hello"}


def test_trace_store_records_runtime_and_tool_call(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    traces = TraceStore(db)

    trace = traces.start_trace(session_id="ses_1", user_input="hello")
    traces.record_tool_call(trace.id, tool_name="echo", arguments={"text": "hello"}, result={"text": "hello"})
    traces.finish_trace(trace.id, status="ok", output="hello")

    stored = traces.get_trace(trace.id)
    calls = traces.get_tool_calls(trace.id)

    assert stored.status == "ok"
    assert stored.output == "hello"
    assert calls[0].tool_name == "echo"
    assert calls[0].result == {"text": "hello"}


def test_runtime_persists_messages_trace_and_uses_active_prompt(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    sessions = SessionManager(db)
    resources = ResourceRegistry(db)
    traces = TraceStore(db)
    tools = ToolRegistry.with_defaults()
    resources.register_resource(
        name="base-system-prompt",
        resource_type="prompt",
        description="Base system prompt",
        content="Answer by echoing the user request.",
        trainable=True,
    )
    runtime = AgentRuntime(sessions=sessions, resources=resources, traces=traces, tools=tools)
    session = sessions.create_session(user_id="user-1", channel="cli", workspace=str(tmp_path))

    result = runtime.run(session.id, "hello")

    assert result.output == "hello"
    messages = sessions.get_messages(session.id)
    assert [(message.role, message.content) for message in messages] == [
        ("user", "hello"),
        ("assistant", "hello"),
    ]
    stored_trace = traces.get_trace(result.trace_id)
    assert stored_trace.status == "ok"
    assert stored_trace.output == "hello"
