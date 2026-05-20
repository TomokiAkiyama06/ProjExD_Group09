"""1台のPCで両プレイヤーを操作する soloモード。

Game を継承し、Builder（プレイヤー1）と Fighter（プレイヤー2）を
1つのプロセスで同時に制御する。デバッグ環境＆発表時のフォールバック。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol

import pygame as pg

from .base_enemy import BaseEnemy
from .base_hud import BaseHud
from .builder import Builder, TowerFactory
from .constants import BGM_MAIN, SCREEN_HEIGHT, SCREEN_WIDTH
from .fighter import Fighter
from .game import Game
from .wave_manager import EnemyFactory, WaveManager, WavePhase
from .world import EffectSink, SoundSink, World

if TYPE_CHECKING:
    from combat.boss_enemy import BossEnemy
    from combat.fighter_skills import BaseSkill
    from combat.weapons import BaseWeapon
    from evolution.evolution_driver import EvolutionDriver


class EvolutionGraphSink(Protocol):
    """EvolutionGraph の描画インターフェース（疎結合用）。"""

    def draw(
        self,
        screen: pg.Surface,
        origin: tuple[int, int],
        size: tuple[int, int] | None = None,
    ) -> None:
        """グラフを描画する。"""


class TowerSelector(Protocol):
    """タワー選択 UI に必要な描画インターフェース。"""

    def draw(
        self,
        screen: pg.Surface,
        builder: Builder,
        world: World,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        """選択 UI とゴーストプレビューを描画する。"""


class WeaponSelector(Protocol):
    """武器切替 UI の描画インターフェース。"""

    def draw(self, screen: pg.Surface, fighter: Fighter, weapon: BaseWeapon) -> None:
        """現在装備中の武器を描画する。"""


BossSpawnedHandler = Callable[["BossEnemy"], None]


class SoloGame(Game):
    """1台で両プレイヤーを操作するゲームモード。"""

    def __init__(  # noqa: PLR0913 - solo モードは合成層なので注入引数が増えやすい
        self,
        tower_factories: dict[str, TowerFactory] | None = None,
        tower_selector: TowerSelector | None = None,
        effects: EffectSink | None = None,
        sound: SoundSink | None = None,
        fighter_weapons: list[BaseWeapon] | None = None,
        fighter_skills: list[BaseSkill] | None = None,
        weapon_selector: WeaponSelector | None = None,
        enemy_factory: EnemyFactory | None = None,
        boss_factory: EnemyFactory | None = None,
        max_wave: int = 3,
        evolution_driver: EvolutionDriver | None = None,
        evolution_graph: EvolutionGraphSink | None = None,
        evolution_graph_origin: tuple[int, int] = (10, 80),
    ) -> None:
        super().__init__()
        self._world: World = World(effects=effects, sound=sound)
        self._builder: Builder = Builder(
            pos=(80.0, SCREEN_HEIGHT - 40.0),
            tower_factories=tower_factories,
        )
        self._fighter: Fighter = Fighter(
            pos=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
            weapons=fighter_weapons,
            skills=fighter_skills,
        )
        self._world.add_player(self._builder)
        self._world.add_player(self._fighter)
        # EvolutionDriver があれば enemy_factory として spawn_enemy を使う
        self._evolution_driver: EvolutionDriver | None = evolution_driver
        if self._evolution_driver is not None:
            self._evolution_driver.set_fortress_pos(self._world.get_fortress().get_pos())
            if enemy_factory is None:
                enemy_factory = self._evolution_driver.spawn_enemy
        self._wave_manager: WaveManager = WaveManager(
            enemy_factory=enemy_factory,
            max_wave=max_wave,
            boss_factory=boss_factory,
        )
        self._hud: BaseHud = BaseHud()
        self._hud.set_max_hp(self._world.get_fortress().get_max_hp())
        self._selector_ui: TowerSelector | None = tower_selector
        self._weapon_ui: WeaponSelector | None = weapon_selector
        self._evolution_graph: EvolutionGraphSink | None = evolution_graph
        self._evolution_graph_origin: tuple[int, int] = evolution_graph_origin
        self._known_enemies: set[int] = set()
        self._generation: int = (
            self._evolution_driver.get_generation() if self._evolution_driver else 0
        )
        self._prev_wave_phase: WavePhase = self._wave_manager.get_phase()
        # BGM 起動（音源未配置でも no-op で安全）
        self._world.get_sound().play_bgm(BGM_MAIN)

    def get_world(self) -> World:
        return self._world

    def get_builder(self) -> Builder:
        return self._builder

    def get_fighter(self) -> Fighter:
        return self._fighter

    def handle_events(self) -> None:
        """QUIT 処理に加え、両プレイヤーに単発イベントを dispatch する。"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._running = False
                continue
            self._builder.handle_event(event, self._world)
            self._fighter.handle_event(event, self._world)

    def update(self, dt: float) -> None:
        """両プレイヤーの入力反映 → World 更新 → ウェーブ進行 → 世代切替。"""
        keys = pg.key.get_pressed()
        self._fighter.update_keys(keys, dt, self._world)

        # Fighter が発射した弾を World へ移送
        bullets = self._fighter.drain_pending_bullets()
        if bullets:
            self._world.add_bullets(bullets)

        # 早期ウェーブ開始リクエストを WaveManager へ反映
        if self._builder.consume_wave_skip():
            self._wave_manager.request_wave_skip()

        # ボス特殊行動と撃破演出
        self._update_bosses(dt)

        self._world.update(dt)
        self._wave_manager.update(self._world, dt)

        # ウェーブ終了（BATTLE → SUMMARY）を検知して進化ループを進める
        self._tick_evolution()

    def draw(self) -> None:
        """World 描画 ＋ HUD オーバーレイ ＋ 各種 UI。"""
        self._world.draw(self._screen)
        self._hud.draw(
            self._screen,
            {
                "core_hp": self._world.get_fortress().get_hp(),
                "core_max_hp": self._world.get_fortress().get_max_hp(),
                "resource": self._builder.get_gold(),
                "wave": self._wave_manager.get_wave(),
                "generation": self._generation,
            },
        )
        if self._selector_ui is not None:
            self._selector_ui.draw(
                self._screen,
                builder=self._builder,
                world=self._world,
                mouse_pos=pg.mouse.get_pos(),
            )
        if self._weapon_ui is not None:
            current_weapon = self._fighter.get_current_weapon()
            if current_weapon is not None:
                self._weapon_ui.draw(self._screen, self._fighter, current_weapon)
        if self._evolution_graph is not None:
            self._evolution_graph.draw(self._screen, self._evolution_graph_origin)

    def _update_bosses(self, dt: float) -> None:
        """BossEnemy の特殊行動と撃破演出を呼ぶ。

        BaseEnemy 互換のため duck-typed に判定する（`combat` への runtime 依存を避ける）。
        """
        enemies: list[BaseEnemy] = self._world.get_enemies()
        # 特殊行動
        for enemy in enemies:
            tick = getattr(enemy, "update_with_world", None)
            if callable(tick):
                tick(dt, self._world)
        # 撃破演出（次フレームで World._enemies から除外される直前に検知）
        for enemy in enemies:
            if not enemy.is_dead():
                if id(enemy) in self._known_enemies:
                    continue
                self._known_enemies.add(id(enemy))
                continue
            death_hook = getattr(enemy, "trigger_death_effect", None)
            if callable(death_hook):
                death_hook(self._world)
        # 既知 ID セットから消えた敵を掃除（メモリリーク防止）
        live_ids = {id(e) for e in enemies if not e.is_dead()}
        self._known_enemies &= live_ids

    def _tick_evolution(self) -> None:
        """WaveManager の BATTLE → SUMMARY 遷移を検知して進化を進める。"""
        current_phase = self._wave_manager.get_phase()
        if (
            self._evolution_driver is not None
            and self._prev_wave_phase is WavePhase.BATTLE
            and current_phase is WavePhase.SUMMARY
        ):
            self._evolution_driver.finalize_wave()
            self._generation = self._evolution_driver.get_generation()
        self._prev_wave_phase = current_phase
