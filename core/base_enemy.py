"""Base enemy class."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import ENEMY_BASE_HP


@dataclass
class BaseEnemy:
    x: float = 0.0
    y: float = 0.0
    hp: int = ENEMY_BASE_HP
    speed: float = 80.0
    reward: int = 1

    def damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def update(self, dt: float) -> None:
        self.x += self.speed * dt

    @property
    def alive(self) -> bool:
        return self.hp > 0
