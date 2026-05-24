from __future__ import annotations

import pytest

from app.core.config import Settings
from app.services.intelligence.task_router import TaskModelRouter
from models.chat import ProviderType
from models.contracts import IntentClassification


class ClassifierStub:
    async def classify(self, text: str) -> IntentClassification:
        return IntentClassification(intent="general", confidence=0.9, labels=["general"])


@pytest.mark.asyncio
async def test_task_router_routes_all_requests_to_openrouter():
    router = TaskModelRouter(
        classifier=ClassifierStub(),
        settings=Settings(openrouter_model="anthropic/claude-sonnet-4.6"),
    )

    _, route = await router.select_route("Hello there", requested_provider=ProviderType.OPENROUTER)

    assert route.provider == ProviderType.OPENROUTER
    assert route.model_name == "anthropic/claude-sonnet-4.6"
    assert "openrouter selected" in route.reason.lower()
