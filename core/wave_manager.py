"""ウェーブ進行管理。

フェーズ：準備 → 戦闘 → 集計 を進めながら、ウェーブ番号に応じて敵をスポーン
する。スポーン対象の敵クラスは外部から差し替えられるよう factory を受け取る。
"""

from __future__ import annotations

import random
from collections.abc import Callable
from enum import Enum

from .base_enemy import BaseEnemy
from .constants import (
    BOSS_DAMAGE_GROWTH_PER_APPEARANCE,
    BOSS_HP_GROWTH_PER_APPEARANCE,
    BOSS_WAVE_MODULO,
    SE_WAVE_END,
    SE_WAVE_START,
    SPECIAL_ENEMY_BASE_PROBABILITY,
    SPECIAL_ENEMY_HP_GROWTH_PER_WAVE,
    SPECIAL_ENEMY_PROBABILITY_GROWTH_PER_WAVE,
    SPECIAL_ENEMY_PROBABILITY_MAX,
)
from .world import World


class WavePhase(str, Enum):
    """ウェーブのフェーズ。"""

    PREPARE = "prepare"
    BATTLE = "battle"
    SUMMARY = "summary"


EnemyFactory = Callable[[tuple[float, float]], BaseEnemy]


def _default_enemy_factory(pos: tuple[float, float]) -> BaseEnemy:
    return BaseEnemy(pos=pos)


class WaveManager:
    """ウェーブ進行を司る。"""

    PREPARE_SECONDS: float = 3.0
    SUMMARY_SECONDS: float = 2.0
    BASE_SPAWN_COUNT: int = 5
    SPAWN_INTERVAL: float = 0.8

    def __init__(
        self,
        enemy_factory: EnemyFactory | None = None,
        max_wave: int = 3,
        boss_factory: EnemyFactory | None = None,
        special_factory: EnemyFactory | None = None,
    ) -> None:
        self._wave: int = 0
        self._max_wave: int = max_wave
        self._phase: WavePhase = WavePhase.PREPARE
        self._phase_timer: float = self.PREPARE_SECONDS
        self._spawn_timer: float = 0.0
        self._remaining_to_spawn: int = 0
        self._factory: EnemyFactory = enemy_factory or _default_enemy_factory
        self._boss_factory: EnemyFactory | None = boss_factory
        # 特殊敵（fast/shielded）の生成 factory。None なら特殊敵は出現しない。
        self._special_factory: EnemyFactory | None = special_factory
        # 次のウェーブ開始時にボスを 1 体追加投入するフラグ
        self._spawn_boss_pending: bool = False

    # ----- accessors -----

    def get_wave(self) -> int:
        """Wave を返す。"""
        return self._wave

    def get_max_wave(self) -> int:
        """Max_wave を返す。"""
        return self._max_wave

    def get_phase(self) -> WavePhase:
        """Phase を返す。"""
        return self._phase

    def get_remaining_to_spawn(self) -> int:
        """Remaining_to_spawn を返す。"""
        return self._remaining_to_spawn

    def is_finished(self) -> bool:
        """全ウェーブを完走した状態。"""
        return self._wave >= self._max_wave and self._phase is WavePhase.SUMMARY

    def request_wave_skip(self) -> bool:
        """PREPARE フェーズなら即 BATTLE に移行する。

        Returns:
            実際にスキップした場合 True。
        """
        if self._phase is not WavePhase.PREPARE:
            return False
        self._phase_timer = 0.0
        return True

    # ----- internal -----

    def _enter_battle(self) -> None:
        self._wave += 1
        self._phase = WavePhase.BATTLE
        self._remaining_to_spawn = self.BASE_SPAWN_COUNT + (self._wave - 1) * 2
        self._spawn_timer = 0.0
        # 5の倍数ウェーブ（BOSS_WAVE_MODULO）でボスを 1 体先頭にスポーン予約
        if self._boss_factory is not None and self._wave % BOSS_WAVE_MODULO == 0:
            self._spawn_boss_pending = True
            self._remaining_to_spawn += 1

    def _special_spawn_probability(self) -> float:
        """現ウェーブでの特殊敵出現率（上限つき、wave1 が基準値）。"""
        prob = SPECIAL_ENEMY_BASE_PROBABILITY + SPECIAL_ENEMY_PROBABILITY_GROWTH_PER_WAVE * max(
            0, self._wave - 1
        )
        return min(SPECIAL_ENEMY_PROBABILITY_MAX, prob)

    def _special_hp_factor(self) -> float:
        """特殊敵 HP のウェーブ倍率（wave1 で 1.0）。"""
        return 1.0 + SPECIAL_ENEMY_HP_GROWTH_PER_WAVE * max(0, self._wave - 1)

    def _boss_appearance(self) -> int:
        """現ウェーブが何回目のボス出現か（wave5→1, wave10→2, ...）。"""
        return self._wave // BOSS_WAVE_MODULO

    def _boss_hp_factor(self) -> float:
        """ボス HP の出現回ごとの倍率（初回で 1.0）。"""
        return 1.0 + BOSS_HP_GROWTH_PER_APPEARANCE * max(0, self._boss_appearance() - 1)

    def _boss_damage_factor(self) -> float:
        """ボス接触ダメージの出現回ごとの倍率（初回で 1.0）。"""
        return 1.0 + BOSS_DAMAGE_GROWTH_PER_APPEARANCE * max(0, self._boss_appearance() - 1)

    def _enter_summary(self) -> None:
        self._phase = WavePhase.SUMMARY
        self._phase_timer = self.SUMMARY_SECONDS

    def _enter_prepare(self) -> None:
        self._phase = WavePhase.PREPARE
        self._phase_timer = self.PREPARE_SECONDS

    # ----- per-frame -----

    def update(self, world: World, dt: float) -> None:
        """フェーズに応じた進行処理。"""
        if self._phase is WavePhase.PREPARE:
            self._phase_timer -= dt
            if self._phase_timer <= 0.0:
                self._enter_battle()
                world.get_sound().play_se(SE_WAVE_START)
            return

        if self._phase is WavePhase.BATTLE:
            spawn_points = world.get_spawn_points()
            if self._remaining_to_spawn > 0 and spawn_points:
                self._spawn_timer -= dt
                if self._spawn_timer <= 0.0:
                    pos = random.choice(spawn_points)
                    if self._spawn_boss_pending and self._boss_factory is not None:
                        boss = self._boss_factory(pos)
                        # ボスは出現回ごとに HP・接触ダメージを強化（fitness 対象外）
                        boss.scale_hp(self._boss_hp_factor())
                        boss.scale_damage(self._boss_damage_factor())
                        world.add_enemy(boss)
                        self._spawn_boss_pending = False
                    elif (
                        self._special_factory is not None
                        and random.random() < self._special_spawn_probability()
                    ):
                        # 特殊敵は通常スポーン枠を置き換える形で、ウェーブ依存で出現
                        special = self._special_factory(pos)
                        special.scale_hp(self._special_hp_factor())
                        world.add_enemy(special)
                    else:
                        world.add_enemy(self._factory(pos))
                    self._remaining_to_spawn -= 1
                    self._spawn_timer = self.SPAWN_INTERVAL
            if self._remaining_to_spawn == 0 and not world.get_enemies():
                self._enter_summary()
                world.get_sound().play_se(SE_WAVE_END)
            return

        if self._phase is WavePhase.SUMMARY:
            self._phase_timer -= dt
            if self._phase_timer <= 0.0:
                if self._wave >= self._max_wave:
                    # 完走。フェーズは SUMMARY のまま保持。
                    return
                self._enter_prepare()
