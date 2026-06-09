from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    workspace TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    resource_type TEXT NOT NULL,
    description TEXT NOT NULL,
    trainable INTEGER NOT NULL,
    active_version_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_versions (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    reason TEXT,
    parent_version_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(resource_id) REFERENCES resources(id)
);

CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    status TEXT NOT NULL,
    output TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    arguments_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(trace_id) REFERENCES traces(id)
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    if db_path.parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    db.commit()
    return db
