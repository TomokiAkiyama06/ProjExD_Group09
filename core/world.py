"""World state and simple physics helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .bullet import Bullet
from .fortress import Fortress


@dataclass
class World:
    fortress: Fortress = field(default_factory=Fortress)
    players: list[object] = field(default_factory=list)
    enemies: list[object] = field(default_factory=list)
    towers: list[object] = field(default_factory=list)
    bullets: list[Bullet] = field(default_factory=list)

    def update(self, dt: float) -> None:
        for entity in [*self.players, *self.enemies, *self.towers, *self.bullets]:
            update = getattr(entity, "update", None)
            if callable(update):
                update(dt)

        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
