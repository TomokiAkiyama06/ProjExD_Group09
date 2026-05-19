"""マップとフィールドの状態。

背景描画、敵の出現口、タワー設置可否判定を担当する。エンティティの一覧
（プレイヤー / 敵 / タワー / 弾）も保持する。
"""

from __future__ import annotations

import contextlib
import math
from typing import Protocol

import pygame as pg

from .base_enemy import BaseEnemy
from .base_player import BasePlayer
from .base_tower import BaseTower
from .bullet import Bullet
from .constants import COLOR_BG, COLOR_TEXT, SCREEN_HEIGHT, SCREEN_WIDTH
from .fortress import Fortress


class EffectSink(Protocol):
    """エフェクト発火点の最小プロトコル（実体は combat.EffectManager）。"""

    def update(self, dt: float) -> None:
        """1 フレーム分のパーティクル更新。"""

    def draw(self, screen: pg.Surface) -> None:
        """全パーティクルを描画。"""

    def spawn_explosion(self, pos: tuple[float, float]) -> None:
        """敵撃破などの爆発エフェクト。"""

    def spawn_hit(self, pos: tuple[float, float]) -> None:
        """ヒット時のフラッシュ。"""

    def spawn_muzzle_flash(
        self,
        pos: tuple[float, float],
        direction: tuple[float, float],
    ) -> None:
        """発射時のマズルフラッシュ。"""

    def spawn_shockwave(
        self,
        pos: tuple[float, float],
        radius: float,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """範囲攻撃の波紋。"""


class _NullEffects:
    """EffectSink を未注入時のフォールバック（全 no-op）。"""

    def update(self, dt: float) -> None:
        _ = dt

    def draw(self, screen: pg.Surface) -> None:
        _ = screen

    def spawn_explosion(
        self,
        pos: tuple[float, float],
        count: int | None = None,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        _ = pos, count, color

    def spawn_hit(
        self,
        pos: tuple[float, float],
        count: int | None = None,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        _ = pos, count, color

    def spawn_muzzle_flash(
        self,
        pos: tuple[float, float],
        direction: tuple[float, float],
        count: int | None = None,
    ) -> None:
        _ = pos, direction, count

    def spawn_shockwave(
        self,
        pos: tuple[float, float],
        radius: float,
        color: tuple[int, int, int] | None = None,
        duration: float | None = None,
    ) -> None:
        _ = pos, radius, color, duration


class World:
    """ワールド（マップ + エンティティ）。"""

    SPAWN_MARKER_RADIUS: int = 8
    TOWER_PLACEMENT_MARGIN: float = 24.0
    FORTRESS_PLACEMENT_MARGIN: float = 60.0

    def __init__(
        self,
        spawn_points: list[tuple[float, float]] | None = None,
        fortress: Fortress | None = None,
        effects: EffectSink | None = None,
    ) -> None:
        if spawn_points is None:
            spawn_points = [
                (40.0, SCREEN_HEIGHT * 0.25),
                (40.0, SCREEN_HEIGHT * 0.50),
                (40.0, SCREEN_HEIGHT * 0.75),
            ]
        self._spawn_points: list[tuple[float, float]] = spawn_points
        self._fortress: Fortress = fortress if fortress is not None else Fortress()
        self._players: list[BasePlayer] = []
        self._enemies: list[BaseEnemy] = []
        self._towers: list[BaseTower] = []
        self._bullets: list[Bullet] = []
        self._effects: EffectSink = effects if effects is not None else _NullEffects()

    # ----- accessors -----

    def get_fortress(self) -> Fortress:
        return self._fortress

    def get_effects(self) -> EffectSink:
        return self._effects

    def get_spawn_points(self) -> list[tuple[float, float]]:
        return list(self._spawn_points)

    def get_players(self) -> list[BasePlayer]:
        return self._players

    def get_enemies(self) -> list[BaseEnemy]:
        return self._enemies

    def get_towers(self) -> list[BaseTower]:
        return self._towers

    def get_bullets(self) -> list[Bullet]:
        return self._bullets

    # ----- mutators -----

    def add_player(self, player: BasePlayer) -> None:
        self._players.append(player)

    def add_enemy(self, enemy: BaseEnemy) -> None:
        self._enemies.append(enemy)

    def add_tower(self, tower: BaseTower) -> None:
        self._towers.append(tower)

    def add_bullet(self, bullet: Bullet) -> None:
        self._bullets.append(bullet)

    def add_bullets(self, bullets: list[Bullet]) -> None:
        self._bullets.extend(bullets)

    # ----- queries -----

    def can_place_tower(self, pos: tuple[float, float]) -> bool:
        """タワーを置けるかどうか。既存タワーとの重なりと拠点との近接を禁止。"""
        x, y = pos
        if x < 0 or x > SCREEN_WIDTH or y < 0 or y > SCREEN_HEIGHT:
            return False
        fx, fy = self._fortress.get_pos()
        if math.hypot(fx - x, fy - y) < self.FORTRESS_PLACEMENT_MARGIN:
            return False
        for t in self._towers:
            tx, ty = t.get_pos()
            if math.hypot(tx - x, ty - y) < self.TOWER_PLACEMENT_MARGIN:
                return False
        return True

    # ----- per-frame -----

    def update(self, dt: float) -> None:
        """エンティティを 1 フレーム分進める。"""
        for player in self._players:
            # 派生クラスが入力を反映する想定。基底では何もしない呼び出しでも可。
            update = getattr(player, "update", None)
            if callable(update):
                # 入力辞書を受けないシグネチャの派生にも備える
                with contextlib.suppress(TypeError):
                    update({"dt": dt})

        for enemy in list(self._enemies):
            enemy.update(self._fortress, dt)
        # 撃破・到達した敵を弾く前に撃破位置のエフェクトを焚く
        for dead in (e for e in self._enemies if e.is_dead()):
            self._effects.spawn_explosion(dead.get_pos())
        self._enemies = [
            e for e in self._enemies if not e.is_dead() and not e.has_reached_fortress()
        ]

        new_bullets: list[Bullet] = []
        for tower in self._towers:
            new_bullets.extend(tower.update(self._enemies))
        self._bullets.extend(new_bullets)

        for bullet in self._bullets:
            bullet.update(dt)
            bullet.check_hit(self._enemies)
        self._bullets = [b for b in self._bullets if not b.is_consumed()]

        # エフェクトのタイムステップ
        self._effects.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """背景・出現口・エンティティを描画する。"""
        screen.fill(COLOR_BG)
        for sp in self._spawn_points:
            pg.draw.circle(
                screen,
                COLOR_TEXT,
                (int(sp[0]), int(sp[1])),
                self.SPAWN_MARKER_RADIUS,
                width=1,
            )
        self._fortress.draw(screen)
        for tower in self._towers:
            tower.draw(screen)
        for enemy in self._enemies:
            enemy.draw(screen)
        for bullet in self._bullets:
            bullet.draw(screen)
        for player in self._players:
            draw = getattr(player, "draw", None)
            if callable(draw):
                draw(screen)
        self._effects.draw(screen)
