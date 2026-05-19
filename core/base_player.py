"""Base player class."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import PLAYER_MAX_HP


@dataclass
class BasePlayer:
    x: float = 0.0
    y: float = 0.0
    hp: int = PLAYER_MAX_HP
    speed: float = 220.0

    def move(self, dx: float, dy: float, dt: float) -> None:
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

    def update(self, dt: float) -> None:
        _ = dt
