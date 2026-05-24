"""Base fortress."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .constants import FORTRESS_MAX_HP


@dataclass
class Fortress:
    x: float = 0.0
    y: float = 0.0
    hp: int = FORTRESS_MAX_HP
    max_hp: int = FORTRESS_MAX_HP

    image: pg.Surface = field(init=False)
    rect: pg.Rect = field(init=False)

    def __post_init__(self) -> None:
        """拠点画像を読み込んで初期化する。"""
        image = pg.image.load(
            Path("assets/fig/fortress.png")
        )

        self.image = pg.transform.scale(
            image,
            (96, 96)
        )

        self.rect = self.image.get_rect(
            center=(int(self.x), int(self.y))
        )

    def draw(self, screen: pg.Surface) -> None:
        """拠点を画像で描画する。"""
        self.rect.center = (
            int(self.x),
            int(self.y)
        )

        screen.blit(self.image, self.rect)

    def damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    @property
    def alive(self) -> bool:
        return self.hp > 0