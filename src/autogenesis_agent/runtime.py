from __future__ import annotations

from autogenesis_agent.domain import RuntimeResult
from autogenesis_agent.resources import ResourceRegistry
from autogenesis_agent.sessions import SessionManager
from autogenesis_agent.tools import ToolRegistry
from autogenesis_agent.tracing import TraceStore


class AgentRuntime:
    """Phase 1 deterministic runtime.

    This keeps Hermes-style runtime boundaries testable without making model
    calls yet. Phase 2 can replace the echo policy with model + SEPL flows.
    """

    def __init__(
        self,
        *,
        sessions: SessionManager,
        resources: ResourceRegistry,
        traces: TraceStore,
        tools: ToolRegistry,
    ):
        self._sessions = sessions
        self._resources = resources
        self._traces = traces
        self._tools = tools

    def run(self, session_id: str, user_input: str) -> RuntimeResult:
        self._sessions.get_session(session_id)
        self._ensure_base_prompt()
        trace = self._traces.start_trace(session_id=session_id, user_input=user_input)
        self._sessions.append_message(session_id, role="user", content=user_input)
        tool_result = self._tools.execute("echo", {"text": user_input})
        self._traces.record_tool_call(
            trace.id,
            tool_name="echo",
            arguments={"text": user_input},
            result=tool_result,
        )
        output = tool_result["text"]
        self._sessions.append_message(session_id, role="assistant", content=output)
        self._traces.finish_trace(trace.id, status="ok", output=output)
        return RuntimeResult(session_id=session_id, trace_id=trace.id, output=output)

    def _ensure_base_prompt(self) -> None:
        existing = self._resources.get_resource_by_name("base-system-prompt")
        if existing is None:
            self._resources.register_resource(
                name="base-system-prompt",
                resource_type="prompt",
                description="Default deterministic Phase 1 system prompt",
                content="Echo user requests while Phase 1 runtime is under construction.",
                trainable=True,
            )
