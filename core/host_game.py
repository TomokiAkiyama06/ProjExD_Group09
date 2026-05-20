"""ホストゲーム（権威サーバ型）。

`SoloGame` を継承して権威サーバの責務を上乗せする:
- `NetServer` を内包し、メインループに合わせて起動/停止
- 受信した input を `player_id` でローカルの Builder / Fighter に dispatch
- ゲーム状態（敵・タワー・プレイヤー・拠点 HP・ウェーブ）を `NET_STATE_HZ` で
  全クライアントへ broadcast

DESIGN.md §2.1 の authoritative-server モデルに準拠。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from network.net_protocol import MSG_EVENT, MSG_INPUT, make_state
    from network.net_server import NetServer
except ImportError:  # pragma: no cover - 開発時のフォールバック
    from ..network.net_protocol import MSG_EVENT, MSG_INPUT, make_state
    from ..network.net_server import NetServer

from .constants import (
    NET_STATE_HZ,
    SERVER_HOST,
    SERVER_PORT,
)
from .solo_game import SoloGame

if TYPE_CHECKING:
    from network.net_server import Address


class HostGame(SoloGame):
    """権威サーバ型ホストゲーム。"""

    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        state_hz: int = NET_STATE_HZ,
        **solo_kwargs: object,
    ) -> None:
        """ホストゲームを初期化する。

        Args:
            host: バインドする IP アドレス。LAN 公開時は "0.0.0.0"。
            port: UDP ポート番号。
            state_hz: state メッセージのブロードキャスト頻度（既定 20Hz）。
            **solo_kwargs: `SoloGame.__init__` に渡すキーワード引数。
        """
        super().__init__(**solo_kwargs)
        self._server: NetServer = NetServer(host=host, port=port)
        self._state_interval: float = 1.0 / max(1, int(state_hz))
        self._time_since_state: float = 0.0
        self._state_seq: int = 0
        self._network_started: bool = False

    # ----- accessors -----

    def get_server(self) -> NetServer:
        return self._server

    def get_bound_address(self) -> Address | None:
        return self._server.get_bound_address()

    def get_state_seq(self) -> int:
        return self._state_seq

    # ----- lifecycle -----

    def start_network(self) -> None:
        """NetServer を起動する（既に起動済みなら何もしない）。"""
        if self._network_started:
            return
        self._server.start()
        self._network_started = True

    def stop_network(self) -> None:
        if not self._network_started:
            return
        self._server.stop()
        self._network_started = False

    def run(self) -> None:
        """メインループ。pygame ループ突入前にネットワークを起動する。"""
        self.start_network()
        try:
            super().run()
        finally:
            self.stop_network()

    # ----- per-frame -----

    def handle_events(self) -> None:
        """共通イベント処理に加え、受信したクライアント input を dispatch する。"""
        super().handle_events()
        for _addr, msg in self._server.poll_messages():
            self._dispatch_remote_message(msg)

    def update(self, dt: float) -> None:
        """SoloGame の状態更新に加えて、ACK/heartbeat と state broadcast を進める。"""
        super().update(dt)
        self._server.update()
        self._time_since_state += dt
        if self._time_since_state >= self._state_interval:
            self._broadcast_state()
            self._time_since_state = 0.0

    # ----- internal -----

    def _dispatch_remote_message(self, msg: dict[str, Any]) -> None:
        """クライアントから受信したメッセージをローカル状態に反映する。"""
        msg_type = msg.get("type")
        if msg_type == MSG_INPUT:
            self._apply_remote_input(msg)
        elif msg_type == MSG_EVENT:
            # 将来：タワー設置などのイベント反映。現状はログ的に保持のみ。
            self._server.get_errors().append(f"received event from client: {msg.get('event')!r}")

    def _apply_remote_input(self, msg: dict[str, Any]) -> None:
        """Input メッセージを player_id ごとにローカルプレイヤーへ反映する。

        player_id == 2（クライアント）からの入力を Fighter の `set_pos` 系で
        反映する。本実装では最小限：move ベクトルだけを fighter._pos に直接
        足し込む（base_player.update と同じ式）。
        """
        player_id = int(msg.get("player_id", 0))
        payload = msg.get("input", {})
        if not isinstance(payload, dict):
            return
        if player_id == 2:
            self._fighter.update(
                {
                    "dt": self.get_dt(),
                    "dx": float(payload.get("move", [0.0, 0.0])[0]),
                    "dy": float(payload.get("move", [0.0, 0.0])[1]),
                }
            )

    def _broadcast_state(self) -> None:
        """現在の World 状態を make_state でシリアライズしてブロードキャストする。"""
        self._state_seq += 1
        world = self.get_world()
        fortress = world.get_fortress()
        enemies = [
            {
                "id": id(enemy),
                "pos": list(enemy.get_pos()),
                "hp": enemy.get_hp(),
            }
            for enemy in world.get_enemies()
        ]
        towers = [
            {
                "id": id(tower),
                "pos": list(tower.get_pos()),
                "damage": tower.get_damage(),
                "range": tower.get_range(),
            }
            for tower in world.get_towers()
        ]
        players = [
            {
                "id": player.get_player_id(),
                "pos": list(player.get_pos()),
                "hp": player.get_hp(),
            }
            for player in world.get_players()
        ]
        state_msg = make_state(
            seq=self._state_seq,
            enemies=enemies,
            towers=towers,
            players=players,
            fortress_hp=fortress.get_hp(),
            wave=self._wave_manager.get_wave(),
        )
        self._server.send_state(state_msg)

    def draw(self) -> None:
        """ホスト側は通常通りローカル描画する。"""
        super().draw()
        # 画面右上にホスト IP / 接続数を小さく表示するのは別 Issue（HUD 拡張）。
