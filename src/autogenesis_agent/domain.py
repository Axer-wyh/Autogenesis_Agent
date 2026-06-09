from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResourceType(str, Enum):
    PROMPT = "prompt"
    SKILL = "skill"
    TOOL = "tool"
    ENVIRONMENT = "environment"
    MEMORY = "memory"
    AGENT_CONFIG = "agent_config"


@dataclass(frozen=True)
class Session:
    id: str
    user_id: str
    channel: str
    workspace: str
    created_at: str


@dataclass(frozen=True)
class Message:
    id: str
    session_id: str
    role: str
    content: str
    created_at: str


@dataclass(frozen=True)
class Resource:
    id: str
    name: str
    resource_type: str
    description: str
    trainable: bool
    active_version_id: str
    created_at: str


@dataclass(frozen=True)
class ResourceVersion:
    id: str
    resource_id: str
    version: int
    content: str
    reason: str | None
    parent_version_id: str | None
    created_at: str


@dataclass(frozen=True)
class Trace:
    id: str
    session_id: str
    user_input: str
    status: str
    output: str | None
    created_at: str
    finished_at: str | None


@dataclass(frozen=True)
class ToolCall:
    id: str
    trace_id: str
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class RuntimeResult:
    session_id: str
    trace_id: str
    output: str
