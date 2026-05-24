"""Bullets and projectiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .constants import BULLET_SPEED, TOWER_BASE_DAMAGE


BULLET_SIZE: tuple[int, int] = (16, 16)


@dataclass
class Bullet:
    """タワーなどから発射される弾を表すクラス。"""

    x: float = 0.0
    y: float = 0.0
    vx: float = BULLET_SPEED
    vy: float = 0.0
    damage: int = TOWER_BASE_DAMAGE
    lifetime: float = 2.0
    image_name: str = "bullet.png"

    image: pg.Surface = field(init=False)
    rect: pg.Rect = field(init=False)

    def __post_init__(self) -> None:
        """画像を読み込み、弾の描画位置を初期化する。"""
        image_path = Path("assets") / "fig" / self.image_name
        self.image = pg.transform.scale(
            pg.image.load(image_path),
            BULLET_SIZE,
        )
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, dt: float) -> None:
        """弾の位置と残り寿命を更新する。"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen: pg.Surface) -> None:
        """弾を画像で描画する。"""
        screen.blit(self.image, self.rect)

    @property
    def alive(self) -> bool:
        """弾がまだ有効かどうかを返す。"""
        return self.lifetime > 0.0