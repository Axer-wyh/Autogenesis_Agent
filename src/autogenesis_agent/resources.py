from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from autogenesis_agent.domain import Resource, ResourceVersion


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class ResourceRegistry:
    def __init__(self, db: sqlite3.Connection):
        self._db = db

    def register_resource(
        self,
        *,
        name: str,
        resource_type: str,
        description: str,
        content: str,
        trainable: bool,
    ) -> Resource:
        resource_id = _id("res")
        version = ResourceVersion(
            id=_id("ver"),
            resource_id=resource_id,
            version=1,
            content=content,
            reason=None,
            parent_version_id=None,
            created_at=_now(),
        )
        resource = Resource(
            id=resource_id,
            name=name,
            resource_type=resource_type,
            description=description,
            trainable=trainable,
            active_version_id=version.id,
            created_at=_now(),
        )
        self._db.execute(
            """
            INSERT INTO resources (id, name, resource_type, description, trainable, active_version_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resource.id,
                resource.name,
                resource.resource_type,
                resource.description,
                int(resource.trainable),
                resource.active_version_id,
                resource.created_at,
            ),
        )
        self._insert_version(version)
        self._db.commit()
        return resource

    def create_version(self, resource_id: str, *, content: str, reason: str) -> ResourceVersion:
        active = self.get_active_version(resource_id)
        version = ResourceVersion(
            id=_id("ver"),
            resource_id=resource_id,
            version=active.version + 1,
            content=content,
            reason=reason,
            parent_version_id=active.id,
            created_at=_now(),
        )
        self._insert_version(version)
        self._db.execute(
            "UPDATE resources SET active_version_id = ? WHERE id = ?",
            (version.id, resource_id),
        )
        self._db.commit()
        return version

    def get_active_version(self, resource_id: str) -> ResourceVersion:
        row = self._db.execute(
            """
            SELECT rv.*
            FROM resources r
            JOIN resource_versions rv ON rv.id = r.active_version_id
            WHERE r.id = ?
            """,
            (resource_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown resource: {resource_id}")
        return self._version_from_row(row)

    def get_resource_by_name(self, name: str) -> Resource | None:
        row = self._db.execute("SELECT * FROM resources WHERE name = ?", (name,)).fetchone()
        if row is None:
            return None
        return Resource(
            id=row["id"],
            name=row["name"],
            resource_type=row["resource_type"],
            description=row["description"],
            trainable=bool(row["trainable"]),
            active_version_id=row["active_version_id"],
            created_at=row["created_at"],
        )

    def _insert_version(self, version: ResourceVersion) -> None:
        self._db.execute(
            """
            INSERT INTO resource_versions
                (id, resource_id, version, content, reason, parent_version_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version.id,
                version.resource_id,
                version.version,
                version.content,
                version.reason,
                version.parent_version_id,
                version.created_at,
            ),
        )

    def _version_from_row(self, row: sqlite3.Row) -> ResourceVersion:
        return ResourceVersion(
            id=row["id"],
            resource_id=row["resource_id"],
            version=int(row["version"]),
            content=row["content"],
            reason=row["reason"],
            parent_version_id=row["parent_version_id"],
            created_at=row["created_at"],
        )
