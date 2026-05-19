"""Tower upgrade helpers."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from ..core.base_tower import BaseTower
except ImportError:
    from core.base_tower import BaseTower


@dataclass(frozen=True)
class TowerUpgrade:
    name: str
    damage_bonus: int = 0
    range_bonus: float = 0.0
    cooldown_multiplier: float = 1.0

    def apply(self, tower: BaseTower) -> None:
        tower.damage += self.damage_bonus
        tower.range += self.range_bonus
        tower.fire_cooldown *= self.cooldown_multiplier
