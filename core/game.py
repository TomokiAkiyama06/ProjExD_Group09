"""Game 基底クラス。

HostGame / ClientGame / SoloGame が共通で継承するメインループの枠組み。
"""

from __future__ import annotations

import pygame as pg

from .constants import COLOR_BG, FPS, SCREEN_HEIGHT, SCREEN_WIDTH


class Game:
    """ゲームの基底クラス。共通のループ構造を提供する。"""

    def __init__(self) -> None:
        pg.init()
        self._screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock: pg.time.Clock = pg.time.Clock()
        self._running: bool = True
        self._dt: float = 0.0

    def get_screen(self) -> pg.Surface:
        """描画対象の Surface を返す。"""
        return self._screen

    def get_dt(self) -> float:
        """直近フレームの経過秒数を返す。"""
        return self._dt

    def is_running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False

    def handle_events(self) -> None:
        """共通イベント処理。QUIT でループ終了。派生クラスはオーバーライド可。"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._running = False

    def update(self) -> None:
        """1フレーム分の状態更新。派生クラスでオーバーライドする。"""
        raise NotImplementedError

    def draw(self) -> None:
        """1フレーム分の描画。派生クラスでオーバーライドする。"""
        raise NotImplementedError

    def run(self) -> None:
        """メインループ。"""
        while self._running:
            self._dt = self._clock.tick(FPS) / 1000.0
            self.handle_events()
            if not self._running:
                break
            self._screen.fill(COLOR_BG)
            self.update()
            self.draw()
            pg.display.flip()
        pg.quit()
