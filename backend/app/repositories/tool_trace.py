from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ToolTraceRepository:
    def __init__(self, database) -> None:
        self.database = database

    async def record(self, session_id: str, payload: dict) -> None:
        await asyncio.to_thread(self._record_sync, session_id, payload)

    def _record_sync(self, session_id: str, payload: dict) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO tool_traces (session_id, tool_name, payload, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, payload.get("tool_name", "unknown"), json.dumps(payload), utcnow_iso()),
            )
            connection.commit()

    async def recent(self, limit: int = 10) -> list[dict]:
        return await asyncio.to_thread(self._recent_sync, limit)

    def _recent_sync(self, limit: int) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT tool_name, payload, created_at
                FROM tool_traces
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        results = []
        for row in rows:
            try:
                payload = json.loads(row["payload"])
            except (json.JSONDecodeError, TypeError):
                payload = {"raw": row["payload"]}
            results.append({
                "tool_name": row["tool_name"],
                "payload": payload,
                "created_at": row["created_at"],
            })
        return results
