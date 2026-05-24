from __future__ import annotations

import httpx

from app.core.config import Settings
from models.contracts import BaseHomeAssistantAdapter, HomeAssistantSummary, HomeDeviceStatus


class HomeAssistantAdapter(BaseHomeAssistantAdapter):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_status(self) -> HomeAssistantSummary:
        if not self.settings.home_assistant_url or not self.settings.home_assistant_token:
            return HomeAssistantSummary(
                status="not_configured",
                endpoint=self.settings.home_assistant_url,
                alerts=["Home Assistant credentials are not configured."],
            )
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.settings.home_assistant_url.rstrip('/')}/api/states",
                    headers={"Authorization": f"Bearer {self.settings.home_assistant_token}"},
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            return HomeAssistantSummary(
                status="error",
                endpoint=self.settings.home_assistant_url,
                alerts=[f"Failed to connect to Home Assistant: {exc}"],
            )
        devices = [
            HomeDeviceStatus(
                entity_id=item["entity_id"],
                state=item.get("state", "unknown"),
                area=item.get("attributes", {}).get("friendly_name"),
                attributes=item.get("attributes", {}),
            )
            for item in data[:10]
        ]
        alerts = [f"{device.entity_id} is {device.state}" for device in devices if device.state not in {"on", "off", "idle"}][:5]
        return HomeAssistantSummary(
            status="ok",
            endpoint=self.settings.home_assistant_url,
            devices=devices,
            alerts=alerts,
        )

