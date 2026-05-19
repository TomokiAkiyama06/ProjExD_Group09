"""Rendering client game mode."""

from __future__ import annotations

from dataclasses import dataclass, field

from .game import Game
from .world import World


@dataclass
class ClientGame(Game):
    world: World = field(default_factory=World)

    def __post_init__(self) -> None:
        Game.__init__(self)

    def update(self, dt: float) -> None:
        self.world.update(dt)
