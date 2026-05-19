"""Versus mode logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VersusMode:
    left_score: int = 0
    right_score: int = 0

    def add_score(self, side: str, amount: int) -> None:
        if side == "left":
            self.left_score += amount
        elif side == "right":
            self.right_score += amount
        else:
            raise ValueError("side must be left or right")
