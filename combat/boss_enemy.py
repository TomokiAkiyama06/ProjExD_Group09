"""Boss enemy."""

from __future__ import annotations

from pathlib import Path

import pygame as pg

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy


BOSS_SIZE: tuple[int, int] = (64, 64)


class BossEnemy(BaseEnemy):
    """ボス敵クラス。"""

    image_name: str = "boss.png"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(hp=180, speed=35.0, reward=10, **kwargs)

        image_path = Path("assets") / "fig" / self.image_name

        self.image = pg.transform.scale(
            pg.image.load(image_path),
            BOSS_SIZE,
        )

        self.rect = self.image.get_rect(
            center=(int(self.x), int(self.y))
        )

    def draw(self, screen: pg.Surface) -> None:
        """ボス敵を画像で描画する。"""
        self.rect.center = (
            int(self.x),
            int(self.y),
        )

        screen.blit(self.image, self.rect)