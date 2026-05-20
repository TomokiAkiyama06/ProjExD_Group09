"""前線役プレイヤーのスキルシステム。

`BaseSkill` 基底と 2 つの具象スキル（`DashAttackSkill` / `AreaAttackSkill`）。
発動は K キー（`Fighter.handle_event` 内で `activate(fighter, world)`）から呼ばれ、
発動後の進行（ダッシュ移動など）は `update(dt, fighter, world)` で進める。
"""

from __future__ import annotations

import math
from typing import ClassVar

import pygame as pg

try:
    from ..core.base_player import BasePlayer
    from ..core.constants import (
        COLOR_EFFECT_SHOCKWAVE,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
        SKILL_AREA_COOLDOWN,
        SKILL_AREA_DAMAGE,
        SKILL_AREA_RADIUS,
        SKILL_DASH_COOLDOWN,
        SKILL_DASH_DAMAGE,
        SKILL_DASH_DISTANCE,
        SKILL_DASH_DURATION,
        SKILL_DASH_HIT_RADIUS,
    )
    from ..core.world import World
except ImportError:
    from core.base_player import BasePlayer
    from core.constants import (
        COLOR_EFFECT_SHOCKWAVE,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
        SKILL_AREA_COOLDOWN,
        SKILL_AREA_DAMAGE,
        SKILL_AREA_RADIUS,
        SKILL_DASH_COOLDOWN,
        SKILL_DASH_DAMAGE,
        SKILL_DASH_DISTANCE,
        SKILL_DASH_DURATION,
        SKILL_DASH_HIT_RADIUS,
    )
    from core.world import World


class BaseSkill:
    """スキル基底クラス。"""

    name: ClassVar[str] = "base"
    cooldown: ClassVar[float] = 1.0

    def __init__(self) -> None:
        self._cooldown_left: float = 0.0

    def get_name(self) -> str:
        return self.name

    def get_cooldown(self) -> float:
        return self.cooldown

    def get_cooldown_left(self) -> float:
        return self._cooldown_left

    def can_use(self) -> bool:
        return self._cooldown_left <= 0

    def is_active(self) -> bool:
        """発動中（複数フレームに渡る効果）かどうか。基底では False。"""
        return False

    def activate(self, fighter: BasePlayer, world: World) -> bool:
        """発動する。クールタイム中は何もせず False。"""
        if not self.can_use():
            return False
        self._cooldown_left = self.cooldown
        self._do_activate(fighter, world)
        return True

    def update(self, dt: float, fighter: BasePlayer, world: World) -> None:
        """毎フレーム呼ばれる。クールタイム減算と発動中の継続処理。"""
        self._cooldown_left = max(0.0, self._cooldown_left - dt)
        self._tick(dt, fighter, world)

    def _do_activate(self, fighter: BasePlayer, world: World) -> None:
        """派生クラスでオーバーライド。発動時の初期化処理。"""

    def _tick(self, dt: float, fighter: BasePlayer, world: World) -> None:
        """派生クラスでオーバーライド。発動中の継続処理。"""


class DashAttackSkill(BaseSkill):
    """ダッシュ攻撃。前方に高速移動し通過した敵にダメージ。"""

    name: ClassVar[str] = "dash"
    cooldown: ClassVar[float] = SKILL_DASH_COOLDOWN

    def __init__(self) -> None:
        super().__init__()
        self._active_remaining: float = 0.0
        self._direction: tuple[float, float] = (1.0, 0.0)
        self._hit_ids: set[int] = set()
        self._invincible: bool = False

    def is_active(self) -> bool:
        return self._active_remaining > 0.0

    def is_invincible(self) -> bool:
        return self._invincible

    def _do_activate(self, fighter: BasePlayer, world: World) -> None:
        _ = world
        get_facing = getattr(fighter, "get_facing", None)
        if callable(get_facing):
            direction = get_facing()
            length = math.hypot(direction[0], direction[1])
            if length > 0:
                self._direction = (direction[0] / length, direction[1] / length)
        self._active_remaining = SKILL_DASH_DURATION
        self._hit_ids = set()
        self._invincible = True

    def _tick(self, dt: float, fighter: BasePlayer, world: World) -> None:
        if self._active_remaining <= 0.0:
            self._invincible = False
            return
        # 高速移動
        speed = SKILL_DASH_DISTANCE / SKILL_DASH_DURATION
        x, y = fighter.get_pos()
        dx, dy = self._direction
        new_x = max(0.0, min(float(SCREEN_WIDTH), x + dx * speed * dt))
        new_y = max(0.0, min(float(SCREEN_HEIGHT), y + dy * speed * dt))
        fighter.set_pos(new_x, new_y)
        # 接触敵にダメージ
        for enemy in world.get_enemies():
            if enemy.is_dead() or id(enemy) in self._hit_ids:
                continue
            ex, ey = enemy.get_pos()
            if math.hypot(ex - new_x, ey - new_y) <= SKILL_DASH_HIT_RADIUS:
                enemy.take_damage(SKILL_DASH_DAMAGE)
                self._hit_ids.add(id(enemy))
                world.get_effects().spawn_hit((ex, ey))
        self._active_remaining = max(0.0, self._active_remaining - dt)
        if self._active_remaining == 0.0:
            self._invincible = False


class AreaAttackSkill(BaseSkill):
    """範囲攻撃。プレイヤー周辺の敵にまとめてダメージを与える。"""

    name: ClassVar[str] = "area"
    cooldown: ClassVar[float] = SKILL_AREA_COOLDOWN

    def _do_activate(self, fighter: BasePlayer, world: World) -> None:
        ox, oy = fighter.get_pos()
        hit_any = False
        for enemy in world.get_enemies():
            if enemy.is_dead():
                continue
            ex, ey = enemy.get_pos()
            if math.hypot(ex - ox, ey - oy) <= SKILL_AREA_RADIUS:
                enemy.take_damage(SKILL_AREA_DAMAGE)
                world.get_effects().spawn_hit((ex, ey))
                hit_any = True
        # 視覚エフェクト（波紋）
        world.get_effects().spawn_shockwave(
            (ox, oy),
            radius=SKILL_AREA_RADIUS,
            color=COLOR_EFFECT_SHOCKWAVE,
        )
        _ = hit_any


SKILL_CYCLE: tuple[type[BaseSkill], ...] = (DashAttackSkill, AreaAttackSkill)


def draw_skill_indicator(
    screen: pg.Surface,
    skill: BaseSkill,
    pos: tuple[int, int],
    size: int = 28,
) -> None:
    """スキルアイコン（残クールタイムの円弧表示）を描画する小ヘルパ。"""
    cx, cy = pos
    if isinstance(skill, DashAttackSkill):
        color = (240, 200, 90)
    elif isinstance(skill, AreaAttackSkill):
        color = (140, 200, 255)
    else:
        color = (200, 200, 200)
    pg.draw.circle(screen, color, (cx, cy), size // 2)
    # 残クールタイム比率に応じて黒い扇形を上から重ねる
    if skill.get_cooldown_left() > 0 and skill.get_cooldown() > 0:
        ratio = skill.get_cooldown_left() / skill.get_cooldown()
        overlay_radius = int(size // 2 * ratio)
        pg.draw.circle(screen, (30, 30, 30), (cx, cy), overlay_radius)
