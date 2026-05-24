from __future__ import annotations

from models.contracts import BaseSentimentHumorScorer, SentimentHumorProfile


class HeuristicSentimentHumorScorer(BaseSentimentHumorScorer):
    POSITIVE = {"great", "awesome", "love", "nice", "thank", "happy"}
    NEGATIVE = {"bad", "hate", "issue", "problem", "angry", "sad"}
    HUMOR = {"joke", "funny", "lol", "haha", "humor", "roast"}

    async def score(self, text: str) -> SentimentHumorProfile:
        tokens = {token.strip(".,!?").lower() for token in text.split()}
        pos = len(tokens & self.POSITIVE)
        neg = len(tokens & self.NEGATIVE)
        humor_hits = len(tokens & self.HUMOR)
        sentiment = "positive" if pos >= neg else "negative" if neg > pos else "neutral"
        humor_level = "high" if humor_hits >= 2 else "medium" if humor_hits == 1 else "low"
        friendliness = min(0.35 + (pos * 0.12), 0.95)
        confidence = min(0.4 + ((pos + neg + humor_hits) * 0.1), 0.9)
        return SentimentHumorProfile(
            sentiment=sentiment,
            humor_level=humor_level,
            friendliness=friendliness,
            confidence=confidence,
        )

