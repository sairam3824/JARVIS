from __future__ import annotations

import httpx

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class WeatherTool(BaseTool):
    definition = ToolDefinition(
        name="weather",
        description="Gets weather recommendations, visibility, and clothing guidance from Open-Meteo.",
        input_schema={"latitude": {"type": "number"}, "longitude": {"type": "number"}},
        category="context",
        capability_tags=["weather", "visibility", "clothing-recommendations"],
        result_type="weather",
    )

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        latitude = args.get("latitude", "12.97")
        longitude = args.get("longitude", "77.59")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,apparent_temperature,weather_code,visibility",
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output=f"Weather API error: {exc}",
                category=self.definition.category,
            )
        current = payload.get("current", {})
        visibility = current.get("visibility", 0)
        clothing = "Light layers" if current.get("temperature_2m", 0) > 26 else "Carry a jacket"
        summary = f"{current.get('temperature_2m', 'N/A')}C with visibility {visibility}m. {clothing} recommended."
        payload["recommendation"] = clothing
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=summary,
            structured_output=payload,
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

