"""特殊敵バリエーション。

- `FastEnemy`: 高速・低HP
- `ShieldedEnemy`: 盾を持ち、盾HPが残っている間はダメージを無効化する
- 旧 `SpecialEnemy` クラス名は `FastEnemy` のエイリアスとして残す（既存呼び出し互換）
"""

from __future__ import annotations

from typing import ClassVar

import pygame as pg

try:
    from ..core.base_enemy import BaseEnemy
    from ..core.constants import (
        COLOR_FAST,
        COLOR_SHIELD,
        COLOR_SHIELDED,
        FAST_ENEMY_DAMAGE,
        FAST_ENEMY_HP,
        FAST_ENEMY_REWARD,
        FAST_ENEMY_SPEED,
        SHIELDED_ENEMY_DAMAGE,
        SHIELDED_ENEMY_HP,
        SHIELDED_ENEMY_REWARD,
        SHIELDED_ENEMY_SHIELD,
        SHIELDED_ENEMY_SPEED,
    )
except ImportError:
    from core.base_enemy import BaseEnemy
    from core.constants import (
        COLOR_FAST,
        COLOR_SHIELD,
        COLOR_SHIELDED,
        FAST_ENEMY_DAMAGE,
        FAST_ENEMY_HP,
        FAST_ENEMY_REWARD,
        FAST_ENEMY_SPEED,
        SHIELDED_ENEMY_DAMAGE,
        SHIELDED_ENEMY_HP,
        SHIELDED_ENEMY_REWARD,
        SHIELDED_ENEMY_SHIELD,
        SHIELDED_ENEMY_SPEED,
    )


class FastEnemy(BaseEnemy):
    """高速・低HP の小型敵。"""

    special_type: ClassVar[str] = "fast"

    def __init__(self, pos: tuple[float, float] = (0.0, 0.0)) -> None:
        super().__init__(
            pos=pos,
            hp=FAST_ENEMY_HP,
            speed=FAST_ENEMY_SPEED,
            damage=FAST_ENEMY_DAMAGE,
            reward=FAST_ENEMY_REWARD,
        )

    def draw(self, screen: pg.Surface) -> None:
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_FAST, (x, y), self.DEFAULT_RADIUS - 2)


class ShieldedEnemy(BaseEnemy):
    """盾を持つ敵。盾HPが残っている間、ダメージはまず盾に吸収される。"""

    special_type: ClassVar[str] = "shielded"

    def __init__(self, pos: tuple[float, float] = (0.0, 0.0)) -> None:
        super().__init__(
            pos=pos,
            hp=SHIELDED_ENEMY_HP,
            speed=SHIELDED_ENEMY_SPEED,
            damage=SHIELDED_ENEMY_DAMAGE,
            reward=SHIELDED_ENEMY_REWARD,
        )
        self._shield: int = SHIELDED_ENEMY_SHIELD
        self._max_shield: int = SHIELDED_ENEMY_SHIELD

    def get_shield(self) -> int:
        return self._shield

    def get_max_shield(self) -> int:
        return self._max_shield

    def has_shield(self) -> bool:
        return self._shield > 0

    def take_damage(self, amount: int) -> None:
        if amount <= 0:
            return
        if self._shield > 0:
            absorbed = min(self._shield, amount)
            self._shield -= absorbed
            amount -= absorbed
        if amount > 0:
            super().take_damage(amount)

    def draw(self, screen: pg.Surface) -> None:
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_SHIELDED, (x, y), self.DEFAULT_RADIUS + 2)
        if self._shield > 0:
            pg.draw.circle(
                screen,
                COLOR_SHIELD,
                (x, y),
                self.DEFAULT_RADIUS + 4,
                width=2,
            )


class SpecialEnemy(FastEnemy):
    """既存呼び出し互換のため `FastEnemy` のエイリアス（旧名）。"""

    special_type: ClassVar[str] = "runner"
