"""Base tower class."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import TOWER_BASE_DAMAGE, TOWER_BASE_RANGE


@dataclass
class BaseTower:
    x: float = 0.0
    y: float = 0.0
    range: float = TOWER_BASE_RANGE
    damage: int = TOWER_BASE_DAMAGE
    fire_cooldown: float = 0.8
    cooldown_left: float = 0.0

    def update(self, dt: float) -> None:
        self.cooldown_left = max(0.0, self.cooldown_left - dt)

    def can_fire(self) -> bool:
        return self.cooldown_left <= 0.0

    def mark_fired(self) -> None:
        self.cooldown_left = self.fire_cooldown
