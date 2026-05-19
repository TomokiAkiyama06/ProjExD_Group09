"""前線役（プレイヤー2）。

WASDで移動、Shiftでダッシュ、Jで通常攻撃（前方に弾を撃つ）、Kでスキル
（クールタイム枠だけ・中身は担当④）、Lで近接タワーの修理（リソース消費）。
"""

from __future__ import annotations

import math
from typing import ClassVar

import pygame as pg

from .base_enemy import BaseEnemy
from .base_player import BasePlayer
from .base_tower import BaseTower
from .bullet import Bullet
from .constants import COLOR_PLAYER, PLAYER_MAX_HP, TOWER_BASE_DAMAGE
from .world import World


class Fighter(BasePlayer):
    """前線役プレイヤー。"""

    BASE_SPEED: float = 220.0
    DASH_MULTIPLIER: float = 1.8
    ATTACK_COOLDOWN: float = 0.4
    ATTACK_DAMAGE: int = TOWER_BASE_DAMAGE
    ATTACK_RANGE: float = 220.0
    SKILL_COOLDOWN: float = 4.0
    REPAIR_AMOUNT: int = 20
    REPAIR_COST: int = 10
    REPAIR_RANGE: float = 40.0
    DEFAULT_RADIUS: int = 14

    MOVE_KEYS: ClassVar[dict[int, tuple[int, int]]] = {
        pg.K_w: (0, -1),
        pg.K_s: (0, 1),
        pg.K_a: (-1, 0),
        pg.K_d: (1, 0),
    }
    DASH_KEYS: ClassVar[tuple[int, ...]] = (pg.K_LSHIFT, pg.K_RSHIFT)

    def __init__(
        self,
        pos: tuple[float, float] | None = None,
        max_hp: int = PLAYER_MAX_HP,
    ) -> None:
        super().__init__(player_id=2, pos=pos, max_hp=max_hp)
        self._speed = self.BASE_SPEED
        self._attack_cooldown_left: float = 0.0
        self._skill_cooldown_left: float = 0.0
        self._is_dashing: bool = False
        self._facing: tuple[float, float] = (1.0, 0.0)
        self._pending_bullets: list[Bullet] = []

    # ----- accessors -----

    def is_dashing(self) -> bool:
        return self._is_dashing

    def get_facing(self) -> tuple[float, float]:
        return self._facing

    def get_attack_cooldown_left(self) -> float:
        return self._attack_cooldown_left

    def get_skill_cooldown_left(self) -> float:
        return self._skill_cooldown_left

    # ----- event-based input -----

    def handle_event(self, event: pg.event.Event, world: World) -> None:
        """単発イベント（J/K/L のキー押下）を処理する。"""
        if event.type != pg.KEYDOWN:
            return
        if event.key == pg.K_j:
            self._try_attack(world)
        elif event.key == pg.K_k:
            self._try_skill()
        elif event.key == pg.K_l:
            self._try_repair(world)

    # ----- continuous input -----

    def update_keys(
        self,
        keys: pg.key.ScancodeWrapper,
        dt: float,
        world: World,
    ) -> None:
        """連続入力（WASD移動、Shiftダッシュ）と内部タイマーを更新する。"""
        _ = world  # 引数を将来の壁判定などに残すために保持
        self._is_dashing = any(keys[k] for k in self.DASH_KEYS)
        speed_mult = self.DASH_MULTIPLIER if self._is_dashing else 1.0

        dx = 0.0
        dy = 0.0
        for key, (kx, ky) in self.MOVE_KEYS.items():
            if keys[key]:
                dx += kx
                dy += ky
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
            self._facing = (dx, dy)
            self.update({"dt": dt, "dx": dx * speed_mult, "dy": dy * speed_mult})

        self._attack_cooldown_left = max(0.0, self._attack_cooldown_left - dt)
        self._skill_cooldown_left = max(0.0, self._skill_cooldown_left - dt)

    # ----- pending output -----

    def drain_pending_bullets(self) -> list[Bullet]:
        """前フレームで生成された弾を取り出して内部キューを空にする。"""
        bullets = self._pending_bullets
        self._pending_bullets = []
        return bullets

    # ----- internal -----

    def _try_attack(self, world: World) -> None:
        if self._attack_cooldown_left > 0:
            return
        self._attack_cooldown_left = self.ATTACK_COOLDOWN
        target = self._find_attack_target(world)
        if target is None:
            return
        self._pending_bullets.append(
            Bullet(pos=self._pos, target=target, damage=self.ATTACK_DAMAGE)
        )

    def _try_skill(self) -> None:
        # スキル本体は担当④が実装する。ここではクールタイムを進めるだけ。
        if self._skill_cooldown_left > 0:
            return
        self._skill_cooldown_left = self.SKILL_COOLDOWN

    def _try_repair(self, world: World) -> None:
        # 近接タワーを修理。リソース管理は今は Fighter 自身が持たず、World 経由で
        # 後付け可能にするため、ここではタワーHP（_max_hp等）を直接いじらない。
        # 担当③で BaseTower にHPを追加した後に詳細実装する想定の枠だけ用意。
        nearest = self._nearest_tower_within_range(world)
        if nearest is None:
            return
        # 枠のみ。実 HP 回復は担当③で BaseTower に HP を追加してから接続する。

    def _find_attack_target(self, world: World) -> BaseEnemy | None:
        x, y = self._pos
        best = None
        best_dist = self.ATTACK_RANGE
        for enemy in world.get_enemies():
            if enemy.is_dead():
                continue
            ex, ey = enemy.get_pos()
            d = math.hypot(ex - x, ey - y)
            if d <= best_dist:
                best_dist = d
                best = enemy
        return best

    def _nearest_tower_within_range(self, world: World) -> BaseTower | None:
        x, y = self._pos
        nearest = None
        nearest_dist = self.REPAIR_RANGE
        for tower in world.get_towers():
            tx, ty = tower.get_pos()
            d = math.hypot(tx - x, ty - y)
            if d <= nearest_dist:
                nearest_dist = d
                nearest = tower
        return nearest

    # ----- draw -----

    def draw(self, screen: pg.Surface) -> None:
        x, y = int(self._pos[0]), int(self._pos[1])
        pg.draw.circle(screen, COLOR_PLAYER, (x, y), self.DEFAULT_RADIUS)
        # 向き表示（短い線）
        fx, fy = self._facing
        end = (int(x + fx * self.DEFAULT_RADIUS), int(y + fy * self.DEFAULT_RADIUS))
        pg.draw.line(screen, COLOR_PLAYER, (x, y), end, width=3)
