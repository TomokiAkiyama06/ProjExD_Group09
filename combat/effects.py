"""Visual effects and particles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Effect:
    x: float
    y: float
    lifetime: float = 0.5

    def update(self, dt: float) -> None:
        self.lifetime -= dt

    @property
    def alive(self) -> bool:
        return self.lifetime > 0.0
