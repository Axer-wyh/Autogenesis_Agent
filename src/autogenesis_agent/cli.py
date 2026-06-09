from __future__ import annotations

import argparse
from pathlib import Path

from autogenesis_agent.resources import ResourceRegistry
from autogenesis_agent.runtime import AgentRuntime
from autogenesis_agent.sessions import SessionManager
from autogenesis_agent.storage import connect
from autogenesis_agent.tools import ToolRegistry
from autogenesis_agent.tracing import TraceStore


def build_runtime(db_path: Path) -> tuple[SessionManager, AgentRuntime]:
    db = connect(db_path)
    sessions = SessionManager(db)
    runtime = AgentRuntime(
        sessions=sessions,
        resources=ResourceRegistry(db),
        traces=TraceStore(db),
        tools=ToolRegistry.with_defaults(),
    )
    return sessions, runtime


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Autogenesis Agent Phase 1 runtime.")
    parser.add_argument("message", help="Message to send to the local deterministic runtime.")
    parser.add_argument("--db", default="workdir/autogenesis.sqlite", help="SQLite database path.")
    parser.add_argument("--workspace", default=".", help="Workspace path attached to the session.")
    args = parser.parse_args(argv)

    sessions, runtime = build_runtime(Path(args.db))
    session = sessions.create_session(user_id="local-user", channel="cli", workspace=args.workspace)
    result = runtime.run(session.id, args.message)
    print(result.output)


if __name__ == "__main__":
    main()
