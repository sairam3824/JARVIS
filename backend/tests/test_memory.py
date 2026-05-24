from pathlib import Path

import pytest

from app.repositories.database import Database
from app.repositories.memory import MemoryRepository


@pytest.mark.asyncio
async def test_memory_repository_ranks_relevant_entries(tmp_path: Path):
    database = Database(tmp_path / "jarvis.db")
    database.initialize()
    repository = MemoryRepository(database)

    await repository.store_fact("session-1", "Jarvis can inspect local files and stream responses.")
    await repository.store_fact("session-2", "The dashboard shows CPU and memory usage.")

    results = await repository.search_relevant("stream local files")

    assert results
    assert "local files" in results[0].content
