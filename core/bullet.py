"""Bullets and projectiles."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import BULLET_SPEED, TOWER_BASE_DAMAGE


@dataclass
class Bullet:
    x: float = 0.0
    y: float = 0.0
    vx: float = BULLET_SPEED
    vy: float = 0.0
    damage: int = TOWER_BASE_DAMAGE
    lifetime: float = 2.0

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

    @property
    def alive(self) -> bool:
        return self.lifetime > 0.0
