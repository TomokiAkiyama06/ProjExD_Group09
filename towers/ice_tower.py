"""Ice tower."""

from __future__ import annotations

try:
    from ..core.base_tower import BaseTower
except ImportError:
    from core.base_tower import BaseTower


class IceTower(BaseTower):
    element = "ice"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(damage=6, fire_cooldown=1.2, **kwargs)
