"""パーティクルエフェクト。

`EffectManager` は `core.world.EffectSink` Protocol に準拠し、ゲーム中の
イベント（敵撃破・命中・発射・スキル発動）に応じてパーティクルや波紋を
スポーンする。
"""

from __future__ import annotations

import math
import random

import pygame as pg

try:
    from ..core.constants import (
        COLOR_EFFECT_EXPLOSION,
        COLOR_EFFECT_HIT,
        COLOR_EFFECT_SHOCKWAVE,
        EFFECT_EXPLOSION_PARTICLES,
        EFFECT_HIT_PARTICLES,
        EFFECT_MUZZLE_PARTICLES,
        EFFECT_SHOCKWAVE_DURATION,
    )
except ImportError:
    from core.constants import (
        COLOR_EFFECT_EXPLOSION,
        COLOR_EFFECT_HIT,
        COLOR_EFFECT_SHOCKWAVE,
        EFFECT_EXPLOSION_PARTICLES,
        EFFECT_HIT_PARTICLES,
        EFFECT_MUZZLE_PARTICLES,
        EFFECT_SHOCKWAVE_DURATION,
    )


class Particle:
    """個別の動的パーティクル。"""

    def __init__(
        self,
        pos: tuple[float, float],
        velocity: tuple[float, float],
        lifetime: float,
        color: tuple[int, int, int],
        radius: int = 3,
    ) -> None:
        self._pos: tuple[float, float] = pos
        self._velocity: tuple[float, float] = velocity
        self._lifetime: float = max(0.0, float(lifetime))
        self._max_lifetime: float = max(0.001, self._lifetime)
        self._color: tuple[int, int, int] = color
        self._radius: int = max(1, int(radius))

    def get_pos(self) -> tuple[float, float]:
        """Pos を返す。"""
        return self._pos

    def get_color(self) -> tuple[int, int, int]:
        """Color を返す。"""
        return self._color

    def is_dead(self) -> bool:
        """Dead かどうかを返す。"""
        return self._lifetime <= 0

    def update(self, dt: float) -> None:
        """1 フレーム分の状態を更新する。"""
        self._pos = (
            self._pos[0] + self._velocity[0] * dt,
            self._pos[1] + self._velocity[1] * dt,
        )
        self._lifetime = max(0.0, self._lifetime - dt)

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        if self.is_dead():
            return
        # 寿命に応じて半径が縮む
        ratio = self._lifetime / self._max_lifetime
        radius = max(1, int(self._radius * ratio))
        pg.draw.circle(
            screen,
            self._color,
            (int(self._pos[0]), int(self._pos[1])),
            radius,
        )


class Shockwave:
    """範囲攻撃の波紋（拡大するリング）。"""

    def __init__(
        self,
        pos: tuple[float, float],
        radius: float,
        color: tuple[int, int, int] = COLOR_EFFECT_SHOCKWAVE,
        duration: float = EFFECT_SHOCKWAVE_DURATION,
    ) -> None:
        self._pos: tuple[float, float] = pos
        self._max_radius: float = max(1.0, float(radius))
        self._color: tuple[int, int, int] = color
        self._remaining: float = max(0.0, float(duration))
        self._duration: float = max(0.001, self._remaining)

    def get_pos(self) -> tuple[float, float]:
        """Pos を返す。"""
        return self._pos

    def get_radius(self) -> float:
        """Radius を返す。"""
        ratio = 1.0 - (self._remaining / self._duration)
        return self._max_radius * ratio

    def is_dead(self) -> bool:
        """Dead かどうかを返す。"""
        return self._remaining <= 0

    def update(self, dt: float) -> None:
        """1 フレーム分の状態を更新する。"""
        self._remaining = max(0.0, self._remaining - dt)

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        if self.is_dead():
            return
        radius = int(self.get_radius())
        if radius < 1:
            return
        pg.draw.circle(
            screen,
            self._color,
            (int(self._pos[0]), int(self._pos[1])),
            radius,
            width=2,
        )


class EffectManager:
    """`core.world.EffectSink` 実装。

    `World` に注入される想定。`spawn_*` でパーティクル / 波紋を追加し、
    `update(dt)` でタイマーを進めて寿命切れを除去、`draw(screen)` で描画する。
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng: random.Random = rng if rng is not None else random.Random()
        self._particles: list[Particle] = []
        self._shockwaves: list[Shockwave] = []

    # ----- accessors（主にテスト用） -----

    def get_particles(self) -> list[Particle]:
        """Particles を返す。"""
        return self._particles

    def get_shockwaves(self) -> list[Shockwave]:
        """Shockwaves を返す。"""
        return self._shockwaves

    # ----- EffectSink 実装 -----

    def update(self, dt: float) -> None:
        """1 フレーム分の状態を更新する。"""
        for p in self._particles:
            p.update(dt)
        for s in self._shockwaves:
            s.update(dt)
        self._particles = [p for p in self._particles if not p.is_dead()]
        self._shockwaves = [s for s in self._shockwaves if not s.is_dead()]

    def draw(self, screen: pg.Surface) -> None:
        """Surface に描画する。"""
        for s in self._shockwaves:
            s.draw(screen)
        for p in self._particles:
            p.draw(screen)

    def spawn_explosion(
        self,
        pos: tuple[float, float],
        count: int = EFFECT_EXPLOSION_PARTICLES,
        color: tuple[int, int, int] = COLOR_EFFECT_EXPLOSION,
    ) -> None:
        """Explosion エフェクトをスポーンする。"""
        for _ in range(count):
            angle = self._rng.random() * 2 * math.pi
            speed = self._rng.uniform(60.0, 220.0)
            vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
            lifetime = self._rng.uniform(0.25, 0.6)
            radius = self._rng.randint(2, 4)
            self._particles.append(Particle(pos, (vx, vy), lifetime, color, radius))

    def spawn_hit(
        self,
        pos: tuple[float, float],
        count: int = EFFECT_HIT_PARTICLES,
        color: tuple[int, int, int] = COLOR_EFFECT_HIT,
    ) -> None:
        """Hit エフェクトをスポーンする。"""
        for _ in range(count):
            angle = self._rng.random() * 2 * math.pi
            speed = self._rng.uniform(40.0, 120.0)
            vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
            lifetime = self._rng.uniform(0.1, 0.3)
            self._particles.append(Particle(pos, (vx, vy), lifetime, color, radius=2))

    def spawn_muzzle_flash(
        self,
        pos: tuple[float, float],
        direction: tuple[float, float],
        count: int = EFFECT_MUZZLE_PARTICLES,
    ) -> None:
        """Muzzle_flash エフェクトをスポーンする。"""
        dx, dy = direction
        norm = math.hypot(dx, dy) or 1.0
        dx, dy = dx / norm, dy / norm
        for _ in range(count):
            spread = self._rng.uniform(-0.4, 0.4)
            cos_s, sin_s = math.cos(spread), math.sin(spread)
            fx = dx * cos_s - dy * sin_s
            fy = dx * sin_s + dy * cos_s
            speed = self._rng.uniform(80.0, 160.0)
            self._particles.append(
                Particle(
                    pos,
                    (fx * speed, fy * speed),
                    lifetime=self._rng.uniform(0.05, 0.18),
                    color=COLOR_EFFECT_HIT,
                    radius=2,
                )
            )

    def spawn_shockwave(
        self,
        pos: tuple[float, float],
        radius: float,
        color: tuple[int, int, int] = COLOR_EFFECT_SHOCKWAVE,
        duration: float = EFFECT_SHOCKWAVE_DURATION,
    ) -> None:
        """Shockwave エフェクトをスポーンする。"""
        self._shockwaves.append(Shockwave(pos, radius, color, duration))
