"""敵基底クラス。

EvolvedEnemy（担当①）、BossEnemy / SpecialEnemy（担当④）が継承する。
基底は拠点に向かって直進する最小実装。
"""

from __future__ import annotations

import math

import pygame as pg

from .constants import COLOR_ENEMY, ENEMY_BASE_DAMAGE, ENEMY_BASE_HP, ENEMY_BASE_REWARD
from .fortress import Fortress


class BaseEnemy:
    """敵基底クラス。拠点へ直進する。"""

    DEFAULT_RADIUS: int = 10
    DEFAULT_SPEED: float = 80.0
    CONTACT_DISTANCE: float = 32.0

    def __init__(
        self,
        pos: tuple[float, float] = (0.0, 0.0),
        hp: int = ENEMY_BASE_HP,
        speed: float = DEFAULT_SPEED,
        damage: int = ENEMY_BASE_DAMAGE,
        reward: int = ENEMY_BASE_REWARD,
    ) -> None:
        self._pos: tuple[float, float] = pos
        self._max_hp: int = hp
        self._hp: int = hp
        self._speed: float = speed
        self._damage: int = damage
        self._reward: int = max(0, reward)
        self._reached: bool = False
        # 速度低下バフ（担当③の氷タワー等で利用）
        self._speed_factor: float = 1.0
        self._slow_remaining: float = 0.0

    @property
    def reward(self) -> int:
        """Reward を行う。"""
        return self._reward

    @reward.setter
    def reward(self, value: int) -> None:
        """Reward を行う。"""
        self.set_reward(value)

    def get_pos(self) -> tuple[float, float]:
        """Pos を返す。"""
        return self._pos

    def set_pos(self, x: float, y: float) -> None:
        """Pos を設定する。"""
        self._pos = (x, y)

    def get_hp(self) -> int:
        """Hp を返す。"""
        return self._hp

    def get_max_hp(self) -> int:
        """Max_hp を返す。"""
        return self._max_hp

    def get_damage(self) -> int:
        """Damage を返す。"""
        return self._damage

    def get_reward(self) -> int:
        """Reward を返す。"""
        return self._reward

    def set_reward(self, value: int) -> None:
        """Reward を設定する。"""
        self._reward = max(0, value)

    def get_speed(self) -> float:
        """Speed を返す。"""
        return self._speed

    def set_speed(self, value: float) -> None:
        """Speed を設定する。"""
        self._speed = max(0.0, value)

    def get_effective_speed(self) -> float:
        """現在の slow バフを反映した実効速度。"""
        return self._speed * self._speed_factor

    def get_speed_factor(self) -> float:
        """Speed_factor を返す。"""
        return self._speed_factor

    def get_slow_remaining(self) -> float:
        """Slow_remaining を返す。"""
        return self._slow_remaining

    def apply_slow(self, factor: float, duration: float) -> None:
        """速度低下バフを適用する。

        既に slow 中の場合は、より強い factor を採用しつつ、残り duration は長い方を採る。
        """
        factor = max(0.0, min(1.0, float(factor)))
        duration = max(0.0, float(duration))
        if duration <= 0.0:
            return
        # より強い slow を優先（factor が小さいほど遅い）
        self._speed_factor = min(self._speed_factor, factor)
        self._slow_remaining = max(self._slow_remaining, duration)

    def has_reached_fortress(self) -> bool:
        """Reached_fortress を持つかどうかを返す。"""
        return self._reached

    def take_damage(self, amount: int) -> None:
        """Take_damage を行う。"""
        if amount <= 0:
            return
        self._hp = max(0, self._hp - amount)

    def is_dead(self) -> bool:
        """Dead かどうかを返す。"""
        return self._hp <= 0

    def update(self, fortress: Fortress, dt: float = 1.0 / 60.0) -> None:
        """拠点方向へ直進移動し、接触時にダメージを与える。"""
        # slow バフのタイマーを進める
        if self._slow_remaining > 0.0:
            self._slow_remaining = max(0.0, self._slow_remaining - dt)
            if self._slow_remaining == 0.0:
                self._speed_factor = 1.0

        if self._reached or self.is_dead():
            return
        fx, fy = fortress.get_pos()
        x, y = self._pos
        vx, vy = fx - x, fy - y
        dist = math.hypot(vx, vy)
        if dist <= self.CONTACT_DISTANCE:
            fortress.take_damage(self._damage)
            self._reached = True
            return
        step = self.get_effective_speed() * dt
        if step >= dist - self.CONTACT_DISTANCE:
            fortress.take_damage(self._damage)
            self._reached = True
            return
        nx = x + (vx / dist) * step
        ny = y + (vy / dist) * step
        self._pos = (nx, ny)

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_ENEMY, (x, y), self.DEFAULT_RADIUS)
