"""前線役プレイヤーが使用する武器バリエーション。

`BaseWeapon` 基底と 3 種類の派生クラスを提供する:
- `MeleeWeapon`: 射程短・ダメージ高・連射普通
- `RangedWeapon`: 射程長・ダメージ普通・連射速い
- `AreaWeapon`: 範囲ダメージ（`AreaBullet`）・連射遅め

各武器は `fire(owner_pos, target, facing) -> list[Bullet]` を返し、SoloGame の
ループから `world.add_bullets(...)` 経由でフィールドに投入される。
"""

from __future__ import annotations

import math
from typing import ClassVar

import pygame as pg

try:
    from ..core.base_enemy import BaseEnemy
    from ..core.bullet import Bullet
    from ..core.constants import (
        COLOR_BULLET,
        COLOR_EFFECT_EXPLOSION,
        WEAPON_AREA_COOLDOWN,
        WEAPON_AREA_DAMAGE,
        WEAPON_AREA_EXPLOSION_RADIUS,
        WEAPON_AREA_RANGE,
        WEAPON_MELEE_COOLDOWN,
        WEAPON_MELEE_DAMAGE,
        WEAPON_MELEE_RANGE,
        WEAPON_RANGED_COOLDOWN,
        WEAPON_RANGED_DAMAGE,
        WEAPON_RANGED_RANGE,
    )
except ImportError:
    from core.base_enemy import BaseEnemy
    from core.bullet import Bullet
    from core.constants import (
        COLOR_BULLET,
        COLOR_EFFECT_EXPLOSION,
        WEAPON_AREA_COOLDOWN,
        WEAPON_AREA_DAMAGE,
        WEAPON_AREA_EXPLOSION_RADIUS,
        WEAPON_AREA_RANGE,
        WEAPON_MELEE_COOLDOWN,
        WEAPON_MELEE_DAMAGE,
        WEAPON_MELEE_RANGE,
        WEAPON_RANGED_COOLDOWN,
        WEAPON_RANGED_DAMAGE,
        WEAPON_RANGED_RANGE,
    )


class AreaBullet(Bullet):
    """着弾時に半径内の敵全員にダメージを与える AOE 弾（AreaWeapon 用）。"""

    def __init__(
        self,
        pos: tuple[float, float],
        target: BaseEnemy,
        damage: int,
        explosion_radius: float,
    ) -> None:
        super().__init__(pos=pos, target=target, damage=damage)
        self._explosion_radius: float = max(0.0, float(explosion_radius))

    def get_explosion_radius(self) -> float:
        """Explosion_radius を返す。"""
        return self._explosion_radius

    def check_hit(self, enemies: list[BaseEnemy] | None = None) -> bool:
        """Hit を判定する。"""
        if self._consumed:
            return False
        if self._target.is_dead():
            self._consumed = True
            return False
        tx, ty = self._target.get_pos()
        x, y = self._pos
        if math.hypot(tx - x, ty - y) > self.HIT_DISTANCE:
            return False
        # 着弾点を中心に範囲ダメージ
        if enemies:
            for enemy in enemies:
                if enemy.is_dead():
                    continue
                ex, ey = enemy.get_pos()
                if math.hypot(ex - tx, ey - ty) <= self._explosion_radius:
                    enemy.take_damage(self._damage)
        else:
            self._target.take_damage(self._damage)
        self._consumed = True
        return True

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_EFFECT_EXPLOSION, (x, y), self.DEFAULT_RADIUS + 1)


class BaseWeapon:
    """武器基底クラス。"""

    name: ClassVar[str] = "base"
    damage: ClassVar[int] = 8
    range_: ClassVar[float] = 100.0
    cooldown: ClassVar[float] = 0.5

    def __init__(self) -> None:
        self._cooldown_left: float = 0.0

    def get_name(self) -> str:
        """Name を返す。"""
        return self.name

    def get_damage(self) -> int:
        """Damage を返す。"""
        return self.damage

    def get_range(self) -> float:
        """Range を返す。"""
        return self.range_

    def get_cooldown(self) -> float:
        """Cooldown を返す。"""
        return self.cooldown

    def get_cooldown_left(self) -> float:
        """Cooldown_left を返す。"""
        return self._cooldown_left

    def is_ready(self) -> bool:
        """Ready かどうかを返す。"""
        return self._cooldown_left <= 0

    def update(self, dt: float) -> None:
        """1 フレーム分の状態を更新する。"""
        self._cooldown_left = max(0.0, self._cooldown_left - dt)

    def find_target(
        self,
        owner_pos: tuple[float, float],
        enemies: list[BaseEnemy],
    ) -> BaseEnemy | None:
        """射程内で最も近い敵を返す。"""
        best: BaseEnemy | None = None
        best_dist = self.range_
        for enemy in enemies:
            if enemy.is_dead():
                continue
            ex, ey = enemy.get_pos()
            d = math.hypot(ex - owner_pos[0], ey - owner_pos[1])
            if d <= best_dist:
                best_dist = d
                best = enemy
        return best

    def fire(
        self,
        owner_pos: tuple[float, float],
        target: BaseEnemy | None,
        facing: tuple[float, float],
    ) -> list[Bullet]:
        """1 回の発射で生成する Bullet のリストを返す（クールタイム中は空）。"""
        _ = facing
        if not self.is_ready() or target is None:
            return []
        self._cooldown_left = self.cooldown
        return self._build_bullets(owner_pos, target)

    def _build_bullets(
        self,
        owner_pos: tuple[float, float],
        target: BaseEnemy,
    ) -> list[Bullet]:
        return [Bullet(pos=owner_pos, target=target, damage=self.damage)]

    def draw_icon(
        self,
        screen: pg.Surface,
        pos: tuple[int, int],
        size: int,
        highlight: bool = False,
    ) -> None:
        """選択 UI 用にアイコンを描画する。派生で色を変える。"""
        color = COLOR_BULLET
        rect = pg.Rect(pos[0], pos[1], size, size)
        pg.draw.rect(screen, color, rect)
        if highlight:
            pg.draw.rect(screen, (240, 240, 240), rect, width=2)


class MeleeWeapon(BaseWeapon):
    """近接武器（射程短・ダメージ高・連射普通）。"""

    name: ClassVar[str] = "melee"
    damage: ClassVar[int] = WEAPON_MELEE_DAMAGE
    range_: ClassVar[float] = WEAPON_MELEE_RANGE
    cooldown: ClassVar[float] = WEAPON_MELEE_COOLDOWN

    def draw_icon(
        self,
        screen: pg.Surface,
        pos: tuple[int, int],
        size: int,
        highlight: bool = False,
    ) -> None:
        """Icon を描画する。"""
        rect = pg.Rect(pos[0], pos[1], size, size)
        pg.draw.rect(screen, (220, 140, 80), rect)
        if highlight:
            pg.draw.rect(screen, (240, 240, 240), rect, width=2)


class RangedWeapon(BaseWeapon):
    """遠距離武器（射程長・ダメージ普通・連射速い）。"""

    name: ClassVar[str] = "ranged"
    damage: ClassVar[int] = WEAPON_RANGED_DAMAGE
    range_: ClassVar[float] = WEAPON_RANGED_RANGE
    cooldown: ClassVar[float] = WEAPON_RANGED_COOLDOWN

    def draw_icon(
        self,
        screen: pg.Surface,
        pos: tuple[int, int],
        size: int,
        highlight: bool = False,
    ) -> None:
        """Icon を描画する。"""
        rect = pg.Rect(pos[0], pos[1], size, size)
        pg.draw.rect(screen, (130, 200, 120), rect)
        if highlight:
            pg.draw.rect(screen, (240, 240, 240), rect, width=2)


class AreaWeapon(BaseWeapon):
    """範囲攻撃武器（範囲ダメージ・連射遅め）。"""

    name: ClassVar[str] = "area"
    damage: ClassVar[int] = WEAPON_AREA_DAMAGE
    range_: ClassVar[float] = WEAPON_AREA_RANGE
    cooldown: ClassVar[float] = WEAPON_AREA_COOLDOWN
    explosion_radius: ClassVar[float] = WEAPON_AREA_EXPLOSION_RADIUS

    def _build_bullets(
        self,
        owner_pos: tuple[float, float],
        target: BaseEnemy,
    ) -> list[Bullet]:
        return [
            AreaBullet(
                pos=owner_pos,
                target=target,
                damage=self.damage,
                explosion_radius=self.explosion_radius,
            )
        ]

    def draw_icon(
        self,
        screen: pg.Surface,
        pos: tuple[int, int],
        size: int,
        highlight: bool = False,
    ) -> None:
        """Icon を描画する。"""
        rect = pg.Rect(pos[0], pos[1], size, size)
        pg.draw.rect(screen, COLOR_EFFECT_EXPLOSION, rect)
        if highlight:
            pg.draw.rect(screen, (240, 240, 240), rect, width=2)


WEAPON_CYCLE: tuple[type[BaseWeapon], ...] = (MeleeWeapon, RangedWeapon, AreaWeapon)
