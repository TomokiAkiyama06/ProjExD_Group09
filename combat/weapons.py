"""Weapon variations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Weapon:
    name: str
    damage: int
    attack_interval: float


SWORD = Weapon(name="sword", damage=8, attack_interval=0.45)
BOW = Weapon(name="bow", damage=6, attack_interval=0.7)
STAFF = Weapon(name="staff", damage=10, attack_interval=1.0)
