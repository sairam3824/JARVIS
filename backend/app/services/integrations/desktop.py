from __future__ import annotations

import asyncio
from pathlib import Path

from models.contracts import BaseDesktopAutomationAdapter


class MacOSDesktopAutomationAdapter(BaseDesktopAutomationAdapter):
    async def open_target(self, target: str, mode: str = "application") -> dict[str, str]:
        try:
            if mode == "url":
                process = await asyncio.create_subprocess_exec("open", target)
            elif mode == "path":
                process = await asyncio.create_subprocess_exec("open", str(Path(target).expanduser()))
            else:
                process = await asyncio.create_subprocess_exec("open", "-a", target)
            await asyncio.wait_for(process.communicate(), timeout=10)
            return {"target": target, "mode": mode, "status": "launched" if process.returncode == 0 else "failed"}
        except asyncio.TimeoutError:
            return {"target": target, "mode": mode, "status": "failed", "reason": "timeout"}
        except OSError as exc:
            return {"target": target, "mode": mode, "status": "failed", "reason": str(exc)}

