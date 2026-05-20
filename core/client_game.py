"""クライアントゲーム（描画専用）。

`Game` を継承し、`NetClient` 経由でホストから受信した state を `StateBuffer` で
60FPS に補間してそのまま画面に描く。ローカル入力は `NET_INPUT_HZ` でホストに
送信する。ゲームロジックは持たない（権威サーバ＝ホスト側）。

DESIGN.md §2.5（補間）と §2.6（接続の流れ）に準拠。
"""

from __future__ import annotations

import time
from typing import Any

import pygame as pg

try:
    from network.net_client import NetClient
    from network.state_buffer import StateBuffer
except ImportError:  # pragma: no cover - 開発時のフォールバック
    from ..network.net_client import NetClient
    from ..network.state_buffer import StateBuffer

from .constants import (
    COLOR_BG,
    COLOR_BULLET,
    COLOR_ENEMY,
    COLOR_FORTRESS,
    COLOR_HP_BAR_BG,
    COLOR_HP_BAR_FG,
    COLOR_PLAYER,
    COLOR_TEXT,
    COLOR_TOWER,
    NET_INPUT_HZ,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SERVER_HOST,
    SERVER_PORT,
)
from .game import Game


class ClientGame(Game):
    """描画専用クライアント。"""

    DEFAULT_ENEMY_RADIUS: int = 10
    DEFAULT_TOWER_RADIUS: int = 16
    DEFAULT_PLAYER_RADIUS: int = 14
    DEFAULT_FORTRESS_RADIUS: int = 36
    HP_BAR_WIDTH: int = 220
    HP_BAR_HEIGHT: int = 12

    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        name: str = "player2",
        input_hz: int = NET_INPUT_HZ,
    ) -> None:
        """クライアントを初期化する。

        Args:
            host: 接続先ホストの IP。
            port: 接続先ポート番号。
            name: ハンドシェイクで送る名前。
            input_hz: 入力送信周波数（既定 30Hz）。
        """
        super().__init__()
        self._client: NetClient = NetClient(host=host, port=port, name=name)
        self._state_buffer: StateBuffer = StateBuffer()
        self._input_interval: float = 1.0 / max(1, int(input_hz))
        self._time_since_input: float = 0.0
        self._connection_lost: bool = False
        self._latest_seq: int = -1
        if not pg.font.get_init():
            pg.font.init()
        self._font: pg.font.Font = pg.font.SysFont(None, 18)

    # ----- accessors -----

    def get_client(self) -> NetClient:
        return self._client

    def get_state_buffer(self) -> StateBuffer:
        return self._state_buffer

    def is_connection_lost(self) -> bool:
        return self._connection_lost

    # ----- lifecycle -----

    def connect(self, timeout: float = 3.0) -> bool:
        """ホストへ接続要求を送り、connect_ok を待つ。"""
        return self._client.connect(timeout=timeout)

    def stop(self) -> None:
        """メインループ停止と NetClient の終了。"""
        super().stop()
        self._client.stop()

    def run(self) -> None:
        """メインループ。接続失敗時は即終了。"""
        if not self.connect():
            self._draw_connection_failed()
            pg.display.flip()
            self._wait_brief()
            pg.quit()
            return
        try:
            super().run()
        finally:
            self._client.stop()

    # ----- per-frame -----

    def update(self, dt: float) -> None:
        """State 受信 → 補間バッファへ push、入力送信、ハートビート更新。"""
        # 受信した state をバッファに蓄積
        latest = self._client.poll_state()
        if latest is not None:
            seq = int(latest.get("seq", 0))
            if seq > self._latest_seq:
                self._state_buffer.push(time.monotonic(), latest)
                self._latest_seq = seq

        # ハートビート / 再送 / タイムアウト判定
        self._client.update()
        if self._client.has_lost_connection():
            self._connection_lost = True
            self._running = False
            return

        # 入力送信（30Hz）
        self._time_since_input += dt
        if self._time_since_input >= self._input_interval:
            self._time_since_input = 0.0
            self._send_local_input()

    def draw(self) -> None:
        """補間 state を取り出してエンティティを描画する。"""
        state = self._state_buffer.get_interpolated(time.monotonic())
        self._screen.fill(COLOR_BG)
        if state is None:
            self._blit_centered("Waiting for host...", y_offset=-20)
            return
        self._draw_fortress(state)
        self._draw_towers(state)
        self._draw_enemies(state)
        self._draw_players(state)
        self._draw_bullets(state)
        self._draw_overlay(state)

    # ----- input ↓ -----

    def _send_local_input(self) -> None:
        """ローカルキー入力を input メッセージにして送信する。"""
        if not self._client.is_connected():
            return
        keys = pg.key.get_pressed()
        dx = (1 if keys[pg.K_d] else 0) - (1 if keys[pg.K_a] else 0)
        dy = (1 if keys[pg.K_s] else 0) - (1 if keys[pg.K_w] else 0)
        payload: dict[str, Any] = {
            "move": [float(dx), float(dy)],
            "attack": bool(keys[pg.K_j]),
            "skill": bool(keys[pg.K_k]),
        }
        self._client.send_input(payload)

    # ----- draw helpers -----

    def _draw_fortress(self, state: dict[str, Any]) -> None:
        # ホスト側の World.fortress と同じ位置（右側中央）にプレースホルダーで描画
        _ = state  # state は将来 fortress 座標を含めた時の予約
        fortress_pos = (SCREEN_WIDTH * 0.85, SCREEN_HEIGHT / 2)
        pg.draw.circle(
            self._screen,
            COLOR_FORTRESS,
            (int(fortress_pos[0]), int(fortress_pos[1])),
            self.DEFAULT_FORTRESS_RADIUS,
        )

    def _draw_towers(self, state: dict[str, Any]) -> None:
        for tower in state.get("towers", []):
            if not isinstance(tower, dict):
                continue
            pos = tower.get("pos") or [0, 0]
            pg.draw.circle(
                self._screen,
                COLOR_TOWER,
                (int(pos[0]), int(pos[1])),
                self.DEFAULT_TOWER_RADIUS,
            )

    def _draw_enemies(self, state: dict[str, Any]) -> None:
        for enemy in state.get("enemies", []):
            if not isinstance(enemy, dict):
                continue
            pos = enemy.get("pos") or [0, 0]
            pg.draw.circle(
                self._screen,
                COLOR_ENEMY,
                (int(pos[0]), int(pos[1])),
                self.DEFAULT_ENEMY_RADIUS,
            )

    def _draw_players(self, state: dict[str, Any]) -> None:
        for player in state.get("players", []):
            if not isinstance(player, dict):
                continue
            pos = player.get("pos") or [0, 0]
            pg.draw.circle(
                self._screen,
                COLOR_PLAYER,
                (int(pos[0]), int(pos[1])),
                self.DEFAULT_PLAYER_RADIUS,
            )

    def _draw_bullets(self, state: dict[str, Any]) -> None:
        for bullet in state.get("bullets", []):
            if not isinstance(bullet, dict):
                continue
            pos = bullet.get("pos") or [0, 0]
            pg.draw.circle(
                self._screen,
                COLOR_BULLET,
                (int(pos[0]), int(pos[1])),
                4,
            )

    def _draw_overlay(self, state: dict[str, Any]) -> None:
        # 拠点 HP バー（左上）
        max_hp = max(1, int(state.get("core_max_hp", 1000)))
        hp = max(0, int(state.get("fortress_hp", 0)))
        bar_x, bar_y = 10, 10
        pg.draw.rect(
            self._screen,
            COLOR_HP_BAR_BG,
            (bar_x, bar_y, self.HP_BAR_WIDTH, self.HP_BAR_HEIGHT),
        )
        ratio = hp / max_hp
        fg_width = int(self.HP_BAR_WIDTH * ratio)
        if fg_width > 0:
            pg.draw.rect(
                self._screen,
                COLOR_HP_BAR_FG,
                (bar_x, bar_y, fg_width, self.HP_BAR_HEIGHT),
            )
        wave = int(state.get("wave", 0))
        pid = self._client.get_player_id()
        self._blit_text(
            f"Core HP {hp}  Wave {wave}  Player {pid}",
            (bar_x + self.HP_BAR_WIDTH + 12, bar_y - 1),
        )

    def _draw_connection_failed(self) -> None:
        self._screen.fill(COLOR_BG)
        self._blit_centered("Failed to connect to host.", y_offset=-10)
        self._blit_centered("Press window close to exit.", y_offset=14)

    def _blit_text(self, text: str, pos: tuple[int, int]) -> None:
        surface = self._font.render(text, True, COLOR_TEXT)
        self._screen.blit(surface, pos)

    def _blit_centered(self, text: str, y_offset: int = 0) -> None:
        surface = self._font.render(text, True, COLOR_TEXT)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self._screen.blit(surface, rect)

    def _wait_brief(self) -> None:
        end = time.monotonic() + 1.5
        while time.monotonic() < end:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
            self._clock.tick(30)
