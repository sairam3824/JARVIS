from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkspaceRepository:
    def __init__(self, database) -> None:
        self.database = database

    async def store_dataset(self, name: str, kind: str, content: str, metadata: dict[str, Any]) -> int:
        return await asyncio.to_thread(self._store_dataset_sync, name, kind, content, metadata)

    def _store_dataset_sync(self, name: str, kind: str, content: str, metadata: dict[str, Any]) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO datasets (name, kind, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, kind, content, json.dumps(metadata), utcnow_iso()),
            )
            connection.commit()
            return int(cursor.lastrowid)

    async def record_analysis(self, source_kind: str, source_id: int | None, analysis_type: str, payload: dict[str, Any]) -> None:
        await asyncio.to_thread(self._record_analysis_sync, source_kind, source_id, analysis_type, payload)

    def _record_analysis_sync(self, source_kind: str, source_id: int | None, analysis_type: str, payload: dict[str, Any]) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO analysis_runs (source_kind, source_id, analysis_type, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source_kind, source_id, analysis_type, json.dumps(payload), utcnow_iso()),
            )
            connection.commit()

    async def store_planner_preview(self, session_id: str | None, kind: str, title: str, payload: dict[str, Any]) -> None:
        await asyncio.to_thread(self._store_planner_preview_sync, session_id, kind, title, payload)

    def _store_planner_preview_sync(self, session_id: str | None, kind: str, title: str, payload: dict[str, Any]) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO planner_previews (session_id, kind, title, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, kind, title, json.dumps(payload), utcnow_iso()),
            )
            connection.commit()

    async def store_qr_result(self, mode: str, payload_text: str | None, decoded_text: str | None, image_base64: str | None) -> None:
        await asyncio.to_thread(self._store_qr_result_sync, mode, payload_text, decoded_text, image_base64)

    def _store_qr_result_sync(self, mode: str, payload_text: str | None, decoded_text: str | None, image_base64: str | None) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO qr_history (mode, payload_text, decoded_text, image_base64, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (mode, payload_text, decoded_text, image_base64, utcnow_iso()),
            )
            connection.commit()

    async def store_integration_snapshot(self, source: str, payload: dict[str, Any]) -> None:
        await asyncio.to_thread(self._store_integration_snapshot_sync, source, payload)

    def _store_integration_snapshot_sync(self, source: str, payload: dict[str, Any]) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO integration_snapshots (source, payload, created_at)
                VALUES (?, ?, ?)
                """,
                (source, json.dumps(payload), utcnow_iso()),
            )
            connection.commit()

    async def store_template(self, category: str, title: str, content: str, metadata: dict[str, Any]) -> None:
        await asyncio.to_thread(self._store_template_sync, category, title, content, metadata)

    def _store_template_sync(self, category: str, title: str, content: str, metadata: dict[str, Any]) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO template_entries (category, title, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category, title, content, json.dumps(metadata), utcnow_iso()),
            )
            connection.commit()

    async def recent_templates(self, limit: int = 8) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._recent_templates_sync, limit)

    def _recent_templates_sync(self, limit: int) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT category, title, content, metadata, created_at
                FROM template_entries
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        results = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            results.append({
                "category": row["category"],
                "title": row["title"],
                "content": row["content"],
                "metadata": metadata,
                "created_at": row["created_at"],
            })
        return results
