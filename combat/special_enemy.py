"""Special enemy variants."""

from __future__ import annotations

from pathlib import Path
import pygame as pg

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy


class SpecialEnemy(BaseEnemy):
    special_type = "runner"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(hp=20, speed=130.0, reward=2, **kwargs)

    def draw(self, screen: pg.Surface) -> None:
        """特殊敵を画像で描画する。"""
        image = pg.image.load(Path("assets/fig/enemy_shielded.png")).convert_alpha()
        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)
