from __future__ import annotations

import sqlite3

from autogenesis_agent.resources import ResourceRegistry
from autogenesis_agent.runtime import AgentRuntime
from autogenesis_agent.sessions import SessionManager
from autogenesis_agent.tools import ToolRegistry
from autogenesis_agent.tracing import TraceStore

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore[misc,assignment]


class CreateSessionRequest(BaseModel):
    user_id: str
    channel: str = "api"
    workspace: str


class ChatRequest(BaseModel):
    message: str


def create_app(db: sqlite3.Connection):
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install the api extra to use the local API: pip install -e '.[api]'") from exc

    sessions = SessionManager(db)
    resources = ResourceRegistry(db)
    traces = TraceStore(db)
    tools = ToolRegistry.with_defaults()
    runtime = AgentRuntime(sessions=sessions, resources=resources, traces=traces, tools=tools)

    app = FastAPI(title="Autogenesis Agent Local API")

    @app.post("/sessions")
    def create_session(request: CreateSessionRequest):
        session = sessions.create_session(
            user_id=request.user_id,
            channel=request.channel,
            workspace=request.workspace,
        )
        return {"id": session.id, "user_id": session.user_id, "channel": session.channel}

    @app.post("/sessions/{session_id}/chat")
    def chat(session_id: str, request: ChatRequest):
        result = runtime.run(session_id, request.message)
        return {"session_id": result.session_id, "trace_id": result.trace_id, "output": result.output}

    return app
