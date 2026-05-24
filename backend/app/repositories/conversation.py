from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from models.chat import ChatMessage, ChatRole


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationRepository:
    def __init__(self, database) -> None:
        self.database = database

    async def append_message(self, session_id: str, role: str, content: str, metadata: dict) -> None:
        await asyncio.to_thread(self._append_message_sync, session_id, role, content, metadata)

    def _append_message_sync(self, session_id: str, role: str, content: str, metadata: dict) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO conversation_messages (session_id, role, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, json.dumps(metadata), utcnow_iso()),
            )
            connection.commit()

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        return await asyncio.to_thread(self._get_messages_sync, session_id)

    def _get_messages_sync(self, session_id: str) -> list[ChatMessage]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content, metadata, created_at
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        results = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            results.append(ChatMessage(
                role=ChatRole(row["role"]),
                content=row["content"],
                metadata=metadata,
                created_at=datetime.fromisoformat(row["created_at"]),
            ))
        return results
