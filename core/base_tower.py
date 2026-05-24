"""Base tower class."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .constants import TOWER_BASE_DAMAGE, TOWER_BASE_RANGE


@dataclass
class BaseTower:
    x: float = 0.0
    y: float = 0.0
    range: float = TOWER_BASE_RANGE
    damage: int = TOWER_BASE_DAMAGE
    fire_cooldown: float = 0.8
    cooldown_left: float = 0.0

    image_name: str = "tower_physical.png"
    image_size: tuple[int, int] = (48, 48)

    image: pg.Surface = field(init=False)
    rect: pg.Rect = field(init=False)

    def __post_init__(self) -> None:
        """タワー画像を読み込んで初期化する。"""
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

    def update(self, dt: float) -> None:
        """タワー状態を更新する。"""
        self.cooldown_left = max(
            0.0,
            self.cooldown_left - dt
        )

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def can_fire(self) -> bool:
        """攻撃可能かを返す。"""
        return self.cooldown_left <= 0.0

    def mark_fired(self) -> None:
        """攻撃後のクールダウンを設定する。"""
        self.cooldown_left = self.fire_cooldown

    def draw(self, screen: pg.Surface) -> None:
        """タワーを画像で描画する。"""
        screen.blit(self.image, self.rect)