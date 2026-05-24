from __future__ import annotations

from models.contracts import BaseRecipePlanner, PlannerPreview


class RecipePlanner(BaseRecipePlanner):
    async def generate_recipe(self, prompt: str, pantry: list[str] | None = None) -> PlannerPreview:
        pantry = pantry or []
        return PlannerPreview(
            kind="recipe",
            title=f"Recipe for {prompt}",
            summary="JARVIS created a quick cooking plan using your pantry and preferences.",
            recipe={
                "ingredients": pantry or ["onion", "tomato", "garlic", "rice"],
                "steps": [
                    f"Prep ingredients for {prompt}",
                    "Saute aromatics and build flavor base",
                    "Cook until tender and season to taste",
                ],
            },
        )

