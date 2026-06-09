from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from autogenesis_agent.domain import Message, Session


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class SessionManager:
    def __init__(self, db: sqlite3.Connection):
        self._db = db

    def create_session(self, *, user_id: str, channel: str, workspace: str) -> Session:
        session = Session(
            id=_id("ses"),
            user_id=user_id,
            channel=channel,
            workspace=workspace,
            created_at=_now(),
        )
        self._db.execute(
            "INSERT INTO sessions (id, user_id, channel, workspace, created_at) VALUES (?, ?, ?, ?, ?)",
            (session.id, session.user_id, session.channel, session.workspace, session.created_at),
        )
        self._db.commit()
        return session

    def get_session(self, session_id: str) -> Session:
        row = self._db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown session: {session_id}")
        return Session(
            id=row["id"],
            user_id=row["user_id"],
            channel=row["channel"],
            workspace=row["workspace"],
            created_at=row["created_at"],
        )

    def append_message(self, session_id: str, *, role: str, content: str) -> Message:
        self.get_session(session_id)
        next_sequence = self._next_sequence(session_id)
        message = Message(
            id=_id("msg"),
            session_id=session_id,
            role=role,
            content=content,
            created_at=_now(),
        )
        self._db.execute(
            """
            INSERT INTO messages (id, session_id, role, content, created_at, sequence)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message.id, message.session_id, message.role, message.content, message.created_at, next_sequence),
        )
        self._db.commit()
        return message

    def get_messages(self, session_id: str) -> list[Message]:
        self.get_session(session_id)
        rows = self._db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY sequence ASC",
            (session_id,),
        ).fetchall()
        return [
            Message(
                id=row["id"],
                session_id=row["session_id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def _next_sequence(self, session_id: str) -> int:
        row = self._db.execute(
            "SELECT COALESCE(MAX(sequence), 0) + 1 AS next_sequence FROM messages WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return int(row["next_sequence"])
