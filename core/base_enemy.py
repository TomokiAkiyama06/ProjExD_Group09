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

    @property
    def reward(self) -> int:
        return self._reward

    @reward.setter
    def reward(self, value: int) -> None:
        self.set_reward(value)

    def get_pos(self) -> tuple[float, float]:
        return self._pos

    def set_pos(self, x: float, y: float) -> None:
        self._pos = (x, y)

    def get_hp(self) -> int:
        return self._hp

    def get_max_hp(self) -> int:
        return self._max_hp

    def get_damage(self) -> int:
        return self._damage

    def get_reward(self) -> int:
        return self._reward

    def set_reward(self, value: int) -> None:
        self._reward = max(0, value)

    def get_speed(self) -> float:
        return self._speed

    def set_speed(self, value: float) -> None:
        self._speed = max(0.0, value)

    def has_reached_fortress(self) -> bool:
        return self._reached

    def take_damage(self, amount: int) -> None:
        if amount <= 0:
            return
        self._hp = max(0, self._hp - amount)

    def is_dead(self) -> bool:
        return self._hp <= 0

    def update(self, fortress: Fortress, dt: float = 1.0 / 60.0) -> None:
        """拠点方向へ直進移動し、接触時にダメージを与える。"""
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
        step = self._speed * dt
        if step >= dist - self.CONTACT_DISTANCE:
            fortress.take_damage(self._damage)
            self._reached = True
            return
        nx = x + (vx / dist) * step
        ny = y + (vy / dist) * step
        self._pos = (nx, ny)

    def draw(self, screen: pg.Surface) -> None:
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_ENEMY, (x, y), self.DEFAULT_RADIUS)
