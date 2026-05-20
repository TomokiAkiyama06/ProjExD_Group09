"""対戦モードのゲームロジック。

2 人がそれぞれの拠点を持ち、敵を送り合う対戦モード。ネットワーク越しの
実プレイは `HostGame` / `ClientGame` の本体実装が必要となるため、本ファイル
ではまずスタンドアロン（同プロセス 2 フィールド）として動作する `VersusGame`
を実装し、ネット結線点として `send_enemy_to_opponent` / `apply_remote_event`
の hook 関数を用意する。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pygame as pg

try:
    from ..core.base_enemy import BaseEnemy
    from ..core.constants import (
        COLOR_BG,
        COLOR_TEXT,
        INITIAL_GOLD,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
        SE_DEFEAT,
        SE_VERSUS_SEND,
        SE_VICTORY,
        VERSUS_FIELD_GAP,
        VERSUS_MAX_WAVE,
        VERSUS_SEND_COST,
    )
    from ..core.fortress import Fortress
    from ..core.wave_manager import EnemyFactory, WaveManager
    from ..core.world import SoundSink, World
except ImportError:
    from core.base_enemy import BaseEnemy
    from core.constants import (
        COLOR_BG,
        COLOR_TEXT,
        INITIAL_GOLD,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
        SE_DEFEAT,
        SE_VERSUS_SEND,
        SE_VICTORY,
        VERSUS_FIELD_GAP,
        VERSUS_MAX_WAVE,
        VERSUS_SEND_COST,
    )
    from core.fortress import Fortress
    from core.wave_manager import EnemyFactory, WaveManager
    from core.world import SoundSink, World


@dataclass
class VersusEvent:
    """ネット越しに送る対戦イベントの最小表現。"""

    type: str
    payload: dict


class PlayerField:
    """対戦中の各プレイヤーが持つ盤面（拠点・World・WaveManager・gold）。"""

    def __init__(  # noqa: PLR0913 - PlayerField の初期化は左右対称構成で 6 引数が自然
        self,
        side: str,
        spawn_points: list[tuple[float, float]],
        fortress_pos: tuple[float, float],
        enemy_factory: EnemyFactory | None = None,
        boss_factory: EnemyFactory | None = None,
        sound: SoundSink | None = None,
    ) -> None:
        self._side: str = side
        self._fortress: Fortress = Fortress(pos=fortress_pos)
        self._world: World = World(
            spawn_points=spawn_points,
            fortress=self._fortress,
            sound=sound,
        )
        self._wave_manager: WaveManager = WaveManager(
            enemy_factory=enemy_factory,
            max_wave=VERSUS_MAX_WAVE,
            boss_factory=boss_factory,
        )
        self._gold: int = INITIAL_GOLD

    def get_side(self) -> str:
        return self._side

    def get_world(self) -> World:
        return self._world

    def get_fortress(self) -> Fortress:
        return self._fortress

    def get_wave_manager(self) -> WaveManager:
        return self._wave_manager

    def get_gold(self) -> int:
        return self._gold

    def set_gold(self, value: int) -> None:
        self._gold = max(0, int(value))

    def add_gold(self, value: int) -> None:
        self._gold = max(0, self._gold + int(value))

    def update(self, dt: float) -> None:
        self._world.update(dt)
        self._wave_manager.update(self._world, dt)


class VersusGame:
    """対戦モードのゲームロジック。

    2 つの `PlayerField` を内部で並列駆動し、敵送信・勝敗判定を担う。
    ネット結線は `apply_remote_event` 経由で外部からイベントを流し込めば
    対応できる構造。
    """

    SIDES: tuple[str, ...] = ("left", "right")

    def __init__(  # noqa: PLR0913 - 対戦モードはネット結線用の注入点が複数ある
        self,
        enemy_factory: EnemyFactory | None = None,
        boss_factory: EnemyFactory | None = None,
        send_cost: int = VERSUS_SEND_COST,
        sound: SoundSink | None = None,
        local_side: str = "left",
        on_send_enemy: Callable[[str, BaseEnemy], None] | None = None,
    ) -> None:
        if local_side not in self.SIDES:
            msg = f"unknown local side: {local_side!r}"
            raise ValueError(msg)
        self._send_cost: int = max(0, int(send_cost))
        self._sound: SoundSink | None = sound
        self._local_side: str = local_side
        # 拠点座標を左右に対称配置
        left_spawn = [
            (SCREEN_WIDTH * 0.20, SCREEN_HEIGHT * 0.30),
            (SCREEN_WIDTH * 0.20, SCREEN_HEIGHT * 0.70),
        ]
        right_spawn = [
            (SCREEN_WIDTH * 0.80, SCREEN_HEIGHT * 0.30),
            (SCREEN_WIDTH * 0.80, SCREEN_HEIGHT * 0.70),
        ]
        self._fields: dict[str, PlayerField] = {
            "left": PlayerField(
                side="left",
                spawn_points=left_spawn,
                fortress_pos=(SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * 0.50),
                enemy_factory=enemy_factory,
                boss_factory=boss_factory,
                sound=sound,
            ),
            "right": PlayerField(
                side="right",
                spawn_points=right_spawn,
                fortress_pos=(SCREEN_WIDTH * 0.92, SCREEN_HEIGHT * 0.50),
                enemy_factory=enemy_factory,
                boss_factory=boss_factory,
                sound=sound,
            ),
        }
        self._winner: str | None = None
        # ネット結線フック：敵送信時に外部（NetServer.send_event 等）へ通知する
        self._on_send_enemy: Callable[[str, BaseEnemy], None] | None = on_send_enemy

    # ----- accessors -----

    def get_field(self, side: str) -> PlayerField:
        if side not in self._fields:
            msg = f"unknown side: {side!r}"
            raise ValueError(msg)
        return self._fields[side]

    def get_sides(self) -> list[str]:
        return list(self.SIDES)

    def get_winner(self) -> str | None:
        return self._winner

    def get_send_cost(self) -> int:
        return self._send_cost

    def get_local_side(self) -> str:
        return self._local_side

    def is_finished(self) -> bool:
        return self._winner is not None

    @staticmethod
    def opponent_of(side: str) -> str:
        return "right" if side == "left" else "left"

    # ----- gameplay -----

    def update(self, dt: float) -> None:
        if self.is_finished():
            return
        for field in self._fields.values():
            field.update(dt)
        self._check_winner()

    def send_enemy(self, sender_side: str, enemy_factory: EnemyFactory) -> bool:
        """`sender_side` のプレイヤーが相手側に敵を 1 体送る。"""
        if self.is_finished():
            return False
        sender = self.get_field(sender_side)
        if sender.get_gold() < self._send_cost:
            return False
        target_side = self.opponent_of(sender_side)
        target = self.get_field(target_side)
        spawn_points = target.get_world().get_spawn_points()
        if not spawn_points:
            return False
        spawn_pos = spawn_points[0]
        enemy = enemy_factory(spawn_pos)
        target.get_world().add_enemy(enemy)
        sender.add_gold(-self._send_cost)
        if self._sound is not None:
            self._sound.play_se(SE_VERSUS_SEND)
        if self._on_send_enemy is not None:
            self._on_send_enemy(target_side, enemy)
        return True

    def apply_remote_event(self, event: VersusEvent) -> None:
        """ネット越しに届いたイベントを内部状態に反映する。

        現状は ``send_enemy`` イベントのみ対応。`payload` に
        `{"target_side", "enemy_factory"}` を含む形式（実プロトコル化は
        ネット担当との結線時に詰める）。
        """
        if event.type == "send_enemy":
            target_side = str(event.payload.get("target_side", ""))
            factory = event.payload.get("enemy_factory")
            if target_side not in self._fields or not callable(factory):
                return
            target = self.get_field(target_side)
            spawn = target.get_world().get_spawn_points()
            if not spawn:
                return
            target.get_world().add_enemy(factory(spawn[0]))

    def _check_winner(self) -> None:
        for side in self.SIDES:
            if self.get_field(side).get_fortress().is_destroyed():
                self._winner = self.opponent_of(side)
                if self._sound is not None:
                    result_se = SE_VICTORY if self._winner == self._local_side else SE_DEFEAT
                    self._sound.play_se(result_se)
                return

    # ----- draw -----

    def draw(self, screen: pg.Surface) -> None:
        """画面を上下に分割し、両プレイヤーのフィールドを並べて描画する。"""
        screen.fill(COLOR_BG)
        half_width = (SCREEN_WIDTH - VERSUS_FIELD_GAP) // 2
        # 左フィールド
        left_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fields["left"].get_world().draw(left_surface)
        screen.blit(left_surface, (0, 0), area=pg.Rect(0, 0, half_width, SCREEN_HEIGHT))
        # 中央セパレータ
        pg.draw.rect(
            screen,
            COLOR_TEXT,
            (half_width, 0, VERSUS_FIELD_GAP, SCREEN_HEIGHT),
        )
        # 右フィールド
        right_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fields["right"].get_world().draw(right_surface)
        screen.blit(
            right_surface,
            (half_width + VERSUS_FIELD_GAP, 0),
            area=pg.Rect(
                half_width + VERSUS_FIELD_GAP,
                0,
                half_width,
                SCREEN_HEIGHT,
            ),
        )
        # 勝敗テキスト
        if self._winner is not None:
            self._draw_result(screen)

    def _draw_result(self, screen: pg.Surface) -> None:
        if not pg.font.get_init():
            pg.font.init()
        font = pg.font.SysFont(None, 48)
        text = font.render(f"WINNER: {self._winner.upper()}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        bg_rect = rect.inflate(40, 24)
        pg.draw.rect(screen, (0, 0, 0), bg_rect)
        pg.draw.rect(screen, COLOR_TEXT, bg_rect, width=2)
        screen.blit(text, rect)


# 旧 API 互換: 既存呼び出しでは VersusMode（スコア加算のみ）が参照される。
@dataclass
class VersusMode:
    """旧 API（左右スコア加算）。新コードは `VersusGame` を使う。"""

    left_score: int = 0
    right_score: int = 0

    def add_score(self, side: str, amount: int) -> None:
        if side == "left":
            self.left_score += amount
        elif side == "right":
            self.right_score += amount
        else:
            msg = "side must be left or right"
            raise ValueError(msg)
