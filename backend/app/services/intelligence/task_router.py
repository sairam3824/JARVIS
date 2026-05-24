from __future__ import annotations

from app.core.config import Settings
from models.chat import ProviderType
from models.contracts import BaseModelRouter, BaseTextClassifier, IntentClassification, ModelRouteResult


class TaskModelRouter(BaseModelRouter):
    def __init__(self, classifier: BaseTextClassifier, settings: Settings) -> None:
        self.classifier = classifier
        self.settings = settings

    async def select_route(
        self,
        prompt: str,
        requested_provider: ProviderType | None = None,
    ) -> tuple[IntentClassification, ModelRouteResult]:
        intent = await self.classifier.classify(prompt)
        provider = ProviderType.OPENROUTER
        model_name = self.settings.openrouter_model
        reason = f"OpenRouter selected for {intent.intent} task routing."
        return intent, ModelRouteResult(provider=provider, task=intent.intent, model_name=model_name, reason=reason)

    def _model_for_provider(self, provider: ProviderType) -> str:
        return self.settings.openrouter_model
