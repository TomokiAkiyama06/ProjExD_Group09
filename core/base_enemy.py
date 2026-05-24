"""Base enemy class."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .constants import ENEMY_BASE_HP


@dataclass
class BaseEnemy:
    x: float = 0.0
    y: float = 0.0
    hp: int = ENEMY_BASE_HP
    speed: float = 80.0
    reward: int = 1

    image_name: str = "enemy.png"
    image_size: tuple[int, int] = (32, 32)

    image: pg.Surface = field(init=False)
    rect: pg.Rect = field(init=False)

    def __post_init__(self) -> None:
        """敵画像を読み込んで初期化する。"""
        image = pg.image.load(
            Path("assets") / "fig" / self.image_name
        )

        self.image = pg.transform.scale(
            image,
            self.image_size
        )

        self.rect = self.image.get_rect(
            center=(int(self.x), int(self.y))
        )

    def damage(self, amount: int) -> None:
        """敵にダメージを与える。"""
        self.hp = max(0, self.hp - amount)

    def update(self, dt: float) -> None:
        """敵の状態を更新する。"""
        self.x += self.speed * dt

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    @property
    def alive(self) -> bool:
        """敵が生存しているかを返す。"""
        return self.hp > 0

    def draw(self, screen: pg.Surface) -> None:
        """敵を画像で描画する。"""
        screen.blit(self.image, self.rect)