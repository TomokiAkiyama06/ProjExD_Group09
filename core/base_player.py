"""プレイヤー基底クラス。

Builder（建築役）と Fighter（前線役）が継承する共通基底。
"""

from __future__ import annotations

import pygame as pg

from .constants import (
    COLOR_PLAYER,
    PLAYER_MAX_HP,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class BasePlayer:
    """プレイヤー基底クラス。"""

    DEFAULT_RADIUS: int = 14
    DEFAULT_SPEED: float = 220.0

    def __init__(
        self,
        player_id: int,
        pos: tuple[float, float] | None = None,
        max_hp: int = PLAYER_MAX_HP,
    ) -> None:
        if pos is None:
            pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self._player_id: int = player_id
        self._pos: tuple[float, float] = pos
        self._max_hp: int = max_hp
        self._hp: int = max_hp
        self._speed: float = self.DEFAULT_SPEED

    def get_player_id(self) -> int:
        """Player_id を返す。"""
        return self._player_id

    def get_pos(self) -> tuple[float, float]:
        """Pos を返す。"""
        return self._pos

    def set_pos(self, x: float, y: float) -> None:
        """Pos を設定する。"""
        self._pos = (x, y)

    def get_hp(self) -> int:
        """Hp を返す。"""
        return self._hp

    def set_hp(self, value: int) -> None:
        """Hp を設定する。"""
        self._hp = max(0, min(self._max_hp, value))

    def update(self, input_state: dict) -> None:
        """入力に応じて状態を更新する。

        入力フォーマットは network/net_protocol.py のメッセージと整合性を保つ
        想定。基底では move 指示の dx/dy を 1 フレームぶん反映するに留める。
        """
        dt = float(input_state.get("dt", 0.0))
        dx = float(input_state.get("dx", 0.0))
        dy = float(input_state.get("dy", 0.0))
        x, y = self._pos
        new_x = max(0.0, min(float(SCREEN_WIDTH), x + dx * self._speed * dt))
        new_y = max(0.0, min(float(SCREEN_HEIGHT), y + dy * self._speed * dt))
        self._pos = (new_x, new_y)

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_PLAYER, (x, y), self.DEFAULT_RADIUS)
