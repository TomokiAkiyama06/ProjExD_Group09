"""Base player class."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .constants import PLAYER_MAX_HP


@dataclass
class BasePlayer:
    x: float = 0.0
    y: float = 0.0
    hp: int = PLAYER_MAX_HP
    speed: float = 220.0

    image_name: str = "player_fighter.png"
    image_size: tuple[int, int] = (32, 32)

    image: pg.Surface = field(init=False)
    rect: pg.Rect = field(init=False)

    def __post_init__(self) -> None:
        """プレイヤー画像を読み込んで初期化する。"""
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

    def move(self, dx: float, dy: float, dt: float) -> None:
        """プレイヤーを移動する。"""
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def update(self, dt: float) -> None:
        """プレイヤー状態を更新する。"""
        _ = dt

    def draw(self, screen: pg.Surface) -> None:
        """プレイヤーを画像で描画する。"""
        screen.blit(self.image, self.rect)