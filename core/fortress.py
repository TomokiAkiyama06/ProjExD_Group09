"""拠点（コア）クラス。

HP を持ち、敵が接触するとダメージを受ける。HP が 0 になると敗北判定。
"""

from __future__ import annotations

import pygame as pg

from .constants import (
    COLOR_FORTRESS,
    COLOR_HP_BAR_BG,
    COLOR_HP_BAR_FG,
    FORTRESS_MAX_HP,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Fortress:
    """拠点クラス。"""

    DEFAULT_RADIUS: int = 36
    HP_BAR_WIDTH: int = 80
    HP_BAR_HEIGHT: int = 6
    HP_BAR_OFFSET: int = 12

    def __init__(
        self,
        pos: tuple[float, float] | None = None,
        max_hp: int = FORTRESS_MAX_HP,
    ) -> None:
        if pos is None:
            pos = (SCREEN_WIDTH * 0.85, SCREEN_HEIGHT / 2)
        self._pos: tuple[float, float] = pos
        self._max_hp: int = max_hp
        self._hp: int = max_hp

    def get_pos(self) -> tuple[float, float]:
        return self._pos

    def set_pos(self, x: float, y: float) -> None:
        self._pos = (x, y)

    def get_hp(self) -> int:
        return self._hp

    def set_hp(self, value: int) -> None:
        self._hp = max(0, min(self._max_hp, value))

    def get_max_hp(self) -> int:
        return self._max_hp

    def take_damage(self, amount: int) -> None:
        """ダメージを受ける（HP は 0 未満にならない）。"""
        if amount <= 0:
            return
        self._hp = max(0, self._hp - amount)

    def is_destroyed(self) -> bool:
        return self._hp <= 0

    def draw(self, screen: pg.Surface) -> None:
        """拠点本体と HP バーを描画する。"""
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_FORTRESS, (x, y), self.DEFAULT_RADIUS)

        # HP バー
        bar_x = x - self.HP_BAR_WIDTH // 2
        bar_y = y - self.DEFAULT_RADIUS - self.HP_BAR_OFFSET
        pg.draw.rect(
            screen,
            COLOR_HP_BAR_BG,
            (bar_x, bar_y, self.HP_BAR_WIDTH, self.HP_BAR_HEIGHT),
        )
        ratio = self._hp / self._max_hp if self._max_hp > 0 else 0.0
        fg_width = int(self.HP_BAR_WIDTH * ratio)
        if fg_width > 0:
            pg.draw.rect(
                screen,
                COLOR_HP_BAR_FG,
                (bar_x, bar_y, fg_width, self.HP_BAR_HEIGHT),
            )
