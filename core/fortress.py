"""Base fortress."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import FORTRESS_MAX_HP


@dataclass
class Fortress:
    hp: int = FORTRESS_MAX_HP
    max_hp: int = FORTRESS_MAX_HP

    def damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    @property
    def alive(self) -> bool:
        return self.hp > 0
