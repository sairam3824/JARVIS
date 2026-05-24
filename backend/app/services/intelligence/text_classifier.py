from __future__ import annotations

from models.contracts import BaseTextClassifier, IntentClassification


class KeywordTextClassifier(BaseTextClassifier):
    KEYWORDS = {
        "analytics": ["csv", "excel", "statistics", "data", "analysis", "trend", "chart"],
        "vision": ["image", "photo", "visual", "screenshot", "qr", "scan"],
        "planner": ["schedule", "plan", "checklist", "daily", "timetable", "task"],
        "automation": ["open app", "launch", "automation", "shortcut", "desktop"],
        "translation": ["translate", "translation", "language"],
        "weather": ["weather", "visibility", "clothes", "temperature"],
        "coding": ["code", "bug", "debug", "generate code"],
    }

    async def classify(self, text: str) -> IntentClassification:
        lowered = text.lower()
        scores: dict[str, int] = {}
        for intent, keywords in self.KEYWORDS.items():
            scores[intent] = sum(1 for keyword in keywords if keyword in lowered)
        best_intent = max(scores, key=scores.get, default="general")
        best_score = scores.get(best_intent, 0)
        labels = [intent for intent, score in scores.items() if score > 0]
        if best_score == 0:
            best_intent = "general"
        confidence = min(0.35 + (best_score * 0.18), 0.95) if best_score else 0.42
        return IntentClassification(intent=best_intent, confidence=confidence, labels=labels)

