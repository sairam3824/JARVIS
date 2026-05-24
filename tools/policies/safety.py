from __future__ import annotations

from pathlib import Path


def is_path_allowed(path: Path, allowed_roots: list[Path]) -> bool:
    try:
        resolved = path.expanduser().resolve(strict=False)
    except (OSError, ValueError):
        return False
    return any(root in resolved.parents or root == resolved for root in allowed_roots)

