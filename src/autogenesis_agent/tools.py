from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class PermissionLevel(str, Enum):
    READ_ONLY = "L0_READ_ONLY"
    LOW_RISK_WRITE = "L1_LOW_RISK_WRITE"
    WORKSPACE_WRITE = "L2_WORKSPACE_WRITE"
    EXTERNAL_SIDE_EFFECT = "L3_EXTERNAL_SIDE_EFFECT"
    CORE_SELF_MODIFY = "L4_CORE_SELF_MODIFY"


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: ToolHandler
    permission: PermissionLevel
    description: str


def echo_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    return {"text": str(arguments.get("text", ""))}


def local_search_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query", ""))
    corpus = arguments.get("corpus", [])
    if not isinstance(corpus, list):
        corpus = []
    matches = [str(item) for item in corpus if query.lower() in str(item).lower()]
    return {"query": query, "matches": matches}


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    @classmethod
    def with_defaults(cls) -> "ToolRegistry":
        registry = cls()
        registry.register("echo", echo_tool, permission=PermissionLevel.READ_ONLY, description="Echo text input")
        registry.register(
            "local_search",
            local_search_tool,
            permission=PermissionLevel.READ_ONLY,
            description="Search a provided in-memory corpus",
        )
        return registry

    def register(
        self,
        name: str,
        handler: ToolHandler,
        *,
        permission: PermissionLevel,
        description: str,
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = ToolDefinition(
            name=name,
            handler=handler,
            permission=permission,
            description=description,
        )

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(name)
        return tool.handler(arguments)
