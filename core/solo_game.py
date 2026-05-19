"""Single-player fallback mode."""

from __future__ import annotations

from dataclasses import dataclass, field

from .game import Game
from .world import World


@dataclass
class SoloGame(Game):
    world: World = field(default_factory=World)

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def draw(self) -> None:
        print("SoloGame scaffold is ready.")
