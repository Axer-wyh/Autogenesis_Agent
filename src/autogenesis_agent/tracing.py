from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from autogenesis_agent.domain import ToolCall, Trace


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class TraceStore:
    def __init__(self, db: sqlite3.Connection):
        self._db = db

    def start_trace(self, *, session_id: str, user_input: str) -> Trace:
        trace = Trace(
            id=_id("trc"),
            session_id=session_id,
            user_input=user_input,
            status="running",
            output=None,
            created_at=_now(),
            finished_at=None,
        )
        self._db.execute(
            """
            INSERT INTO traces (id, session_id, user_input, status, output, created_at, finished_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (trace.id, trace.session_id, trace.user_input, trace.status, trace.output, trace.created_at, trace.finished_at),
        )
        self._db.commit()
        return trace

    def finish_trace(self, trace_id: str, *, status: str, output: str) -> Trace:
        finished_at = _now()
        self._db.execute(
            "UPDATE traces SET status = ?, output = ?, finished_at = ? WHERE id = ?",
            (status, output, finished_at, trace_id),
        )
        self._db.commit()
        return self.get_trace(trace_id)

    def record_tool_call(
        self,
        trace_id: str,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        result: dict[str, Any],
    ) -> ToolCall:
        call = ToolCall(
            id=_id("tlc"),
            trace_id=trace_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            created_at=_now(),
        )
        self._db.execute(
            """
            INSERT INTO tool_calls (id, trace_id, tool_name, arguments_json, result_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                call.id,
                call.trace_id,
                call.tool_name,
                json.dumps(call.arguments, ensure_ascii=False, sort_keys=True),
                json.dumps(call.result, ensure_ascii=False, sort_keys=True),
                call.created_at,
            ),
        )
        self._db.commit()
        return call

    def get_trace(self, trace_id: str) -> Trace:
        row = self._db.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown trace: {trace_id}")
        return Trace(
            id=row["id"],
            session_id=row["session_id"],
            user_input=row["user_input"],
            status=row["status"],
            output=row["output"],
            created_at=row["created_at"],
            finished_at=row["finished_at"],
        )

    def get_tool_calls(self, trace_id: str) -> list[ToolCall]:
        rows = self._db.execute(
            "SELECT * FROM tool_calls WHERE trace_id = ? ORDER BY created_at ASC",
            (trace_id,),
        ).fetchall()
        return [
            ToolCall(
                id=row["id"],
                trace_id=row["trace_id"],
                tool_name=row["tool_name"],
                arguments=json.loads(row["arguments_json"]),
                result=json.loads(row["result_json"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]
