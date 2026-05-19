"""Lightning tower."""

from __future__ import annotations

try:
    from ..core.base_tower import BaseTower
except ImportError:
    from core.base_tower import BaseTower


class LightningTower(BaseTower):
    element = "lightning"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(damage=9, fire_cooldown=0.55, **kwargs)
