from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timezone

from models.contracts import MemoryRecord


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryRepository:
    def __init__(self, database) -> None:
        self.database = database

    async def store_fact(self, session_id: str, content: str, kind: str = "fact") -> None:
        await asyncio.to_thread(self._store_fact_sync, session_id, content, kind)

    def _store_fact_sync(self, session_id: str, content: str, kind: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO memory_records (session_id, kind, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, kind, content, utcnow_iso()),
            )
            connection.commit()

    async def search_relevant(self, query: str) -> list[MemoryRecord]:
        return await asyncio.to_thread(self._search_relevant_sync, query)

    def _search_relevant_sync(self, query: str) -> list[MemoryRecord]:
        tokens = Counter(token.lower() for token in query.split() if token.strip())
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT kind, content
                FROM memory_records
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()
        ranked: list[MemoryRecord] = []
        for row in rows:
            score = sum(tokens[token.lower()] for token in row["content"].split() if token.lower() in tokens)
            if score:
                ranked.append(MemoryRecord(kind=row["kind"], content=row["content"], relevance=float(score)))
        return sorted(ranked, key=lambda item: item.relevance, reverse=True)[:5]
