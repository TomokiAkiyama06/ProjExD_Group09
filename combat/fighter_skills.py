"""Frontline player skills."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FighterSkill:
    name: str
    cooldown: float
    power: int


SLASH = FighterSkill(name="slash", cooldown=0.4, power=10)
DASH = FighterSkill(name="dash", cooldown=2.0, power=0)
