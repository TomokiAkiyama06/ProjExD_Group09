"""1台のPCで両プレイヤーを操作する soloモード。

Game を継承し、Builder（プレイヤー1）と Fighter（プレイヤー2）を
1つのプロセスで同時に制御する。デバッグ環境＆発表時のフォールバック。
"""

from __future__ import annotations

from typing import Protocol

import pygame as pg

from .base_hud import BaseHud
from .builder import Builder, TowerFactory
from .constants import SCREEN_HEIGHT, SCREEN_WIDTH
from .fighter import Fighter
from .game import Game
from .wave_manager import WaveManager
from .world import World


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


class SoloGame(Game):
    """1台で両プレイヤーを操作するゲームモード。"""

    def __init__(
        self,
        tower_factories: dict[str, TowerFactory] | None = None,
        tower_selector: TowerSelector | None = None,
    ) -> None:
        super().__init__()
        self._world: World = World()
        self._builder: Builder = Builder(
            pos=(80.0, SCREEN_HEIGHT - 40.0),
            tower_factories=tower_factories,
        )
        self._fighter: Fighter = Fighter(pos=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self._world.add_player(self._builder)
        self._world.add_player(self._fighter)
        self._wave_manager: WaveManager = WaveManager()
        self._hud: BaseHud = BaseHud()
        self._hud.set_max_hp(self._world.get_fortress().get_max_hp())
        self._selector_ui: TowerSelector | None = tower_selector
        self._generation: int = 0

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
        """両プレイヤーの入力反映 → World 更新 → ウェーブ進行。"""
        keys = pg.key.get_pressed()
        self._fighter.update_keys(keys, dt, self._world)

        # Fighter が発射した弾を World へ移送
        bullets = self._fighter.drain_pending_bullets()
        if bullets:
            self._world.add_bullets(bullets)

        # 早期ウェーブ開始リクエストを WaveManager へ反映
        if self._builder.consume_wave_skip():
            self._wave_manager.request_wave_skip()

        self._world.update(dt)
        self._wave_manager.update(self._world, dt)

    def draw(self) -> None:
        """World 描画 ＋ HUD オーバーレイ ＋ タワー選択 UI。"""
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
