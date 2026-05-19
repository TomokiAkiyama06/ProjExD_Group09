"""Fire tower."""

from __future__ import annotations

try:
    from ..core.base_tower import BaseTower
except ImportError:
    from core.base_tower import BaseTower


class FireTower(BaseTower):
    element = "fire"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(damage=12, fire_cooldown=1.0, **kwargs)
