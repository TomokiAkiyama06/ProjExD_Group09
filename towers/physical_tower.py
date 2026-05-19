"""Physical tower."""

from __future__ import annotations

try:
    from ..core.base_tower import BaseTower
except ImportError:
    from core.base_tower import BaseTower


class PhysicalTower(BaseTower):
    element = "physical"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(damage=10, fire_cooldown=0.8, **kwargs)
