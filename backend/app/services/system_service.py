from __future__ import annotations

import logging
import platform

import psutil

from models.contracts import SystemSnapshot

logger = logging.getLogger(__name__)


class SystemService:
    def __init__(self, tool_registry, trace_repository) -> None:
        self.tool_registry = tool_registry
        self.trace_repository = trace_repository

    async def snapshot(self) -> SystemSnapshot:
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_percent = memory.percent
            available_memory_mb = round(memory.available / (1024 * 1024), 2)
        except Exception:
            logger.warning("Failed to read system metrics")
            cpu_percent = 0.0
            memory_percent = 0.0
            available_memory_mb = 0.0
        try:
            traces = await self.trace_repository.recent()
        except Exception:
            logger.warning("Failed to read recent traces")
            traces = []
        recent_logs = [
            f"{trace['tool_name']} @ {trace['created_at']}"
            for trace in traces
        ]
        return SystemSnapshot(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            available_memory_mb=available_memory_mb,
            running_tools=[tool.name for tool in self.tool_registry.definitions()],
            recent_logs=[f"{platform.node()}: {line}" for line in recent_logs],
        )
