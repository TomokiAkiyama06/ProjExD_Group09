"""Single-player fallback mode."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame as pg

from .constants import SCREEN_HEIGHT, SCREEN_WIDTH
from .game import Game
from .world import World


@dataclass
class SoloGame(Game):
    """1人プレイ用のゲームモード。"""

    world: World = field(default_factory=World)

    def update(self, dt: float) -> None:
        """ワールドの状態を更新する。"""
        self.world.update(dt)

    def draw(self) -> None:
        """1人プレイ用の画面を描画する。"""
        screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Co-evolution Fortress - Solo")

        running = True
        clock = pg.time.Clock()

        while running:
            dt = clock.tick(60) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            self.update(dt)

            screen.fill((30, 30, 30))
            self.world.draw(screen)
            pg.display.flip()

        pg.quit()