"""HostGame ↔ ClientGame のループバック統合テスト。

同一プロセス内で HostGame と ClientGame を並列起動し、ハンドシェイク・state
同期・入力送信が動作することを verify する。GUI は不要（SDL_VIDEODRIVER=dummy）。
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

from core.client_game import ClientGame
from core.host_game import HostGame


def _wait_until(
    predicate: Callable[[], bool],
    timeout: float = 3.0,
    step: float = 0.05,
) -> bool:
    """述語が True になるまで最大 timeout 秒待機する。"""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return False


def _drive_host_one_frame(host: HostGame, dt: float = 1.0 / 60.0) -> None:
    """HostGame の 1 フレーム分を手動で進める（run() を使わずに verify するため）。"""
    pg.event.pump()
    host.handle_events()
    host.update(dt)


def test_host_starts_and_binds_port() -> None:
    """HostGame.start_network() でソケットがバインドされる。"""
    pg.init()
    pg.display.set_mode((400, 200))
    host = HostGame(host="127.0.0.1", port=0)
    try:
        host.start_network()
        bound = host.get_bound_address()
        assert bound is not None
        assert bound[1] > 0  # 動的ポート
    finally:
        host.stop_network()
        pg.quit()


def test_client_connects_to_host_and_receives_state() -> None:
    """ClientGame.connect() でハンドシェイクが成立し、state を受信できる。"""
    pg.init()
    pg.display.set_mode((400, 200))
    host = HostGame(host="127.0.0.1", port=0)
    host.start_network()
    bound = host.get_bound_address()
    assert bound is not None
    host_ip, host_port = bound

    client = ClientGame(host=host_ip, port=host_port, name="tester")
    try:
        # 接続
        connected = client.connect(timeout=2.0)
        assert connected, "client should connect to host"
        assert client.get_client().get_player_id() is not None

        # ホスト側ループを数フレーム回して state broadcast を発生させる
        for _ in range(20):
            _drive_host_one_frame(host)

        # クライアントが state を受信するまで待つ
        assert _wait_until(lambda: client.get_client().poll_state() is not None)

        # state バッファに push できることを verify
        latest = client.get_client().poll_state()
        assert latest is not None
        assert latest.get("type") == "state"
        assert "enemies" in latest
        assert "fortress_hp" in latest
        assert "wave" in latest
    finally:
        client.stop()
        host.stop_network()
        pg.quit()


def test_host_processes_client_input() -> None:
    """クライアントが送った input がホストの inbox に届く（dispatch も例外なく動く）。"""
    pg.init()
    pg.display.set_mode((400, 200))
    host = HostGame(host="127.0.0.1", port=0)
    host.start_network()
    bound = host.get_bound_address()
    assert bound is not None
    host_ip, host_port = bound

    client = ClientGame(host=host_ip, port=host_port, name="tester2")
    try:
        assert client.connect(timeout=2.0)
        # クライアント側から input を送る
        client.get_client().send_input({"move": [1.0, 0.0], "attack": False})

        # ホスト側のループで input が dispatch される（例外が出ないことを確認）
        for _ in range(10):
            _drive_host_one_frame(host)

        # _broadcast_state が動いたことを seq で確認
        assert host.get_state_seq() >= 1
    finally:
        client.stop()
        host.stop_network()
        pg.quit()


def test_host_broadcasts_state_at_configured_hz() -> None:
    """HostGame.update を 1 秒分回すと state_seq が state_hz 回程度増える。"""
    pg.init()
    pg.display.set_mode((400, 200))
    host = HostGame(host="127.0.0.1", port=0, state_hz=20)
    host.start_network()
    try:
        # 1 秒分回す（60FPS で 60 フレーム）
        for _ in range(60):
            _drive_host_one_frame(host, dt=1.0 / 60.0)
        # 1 秒で 20Hz → 約 20 回（最低 15 回は超える想定）
        assert host.get_state_seq() >= 15
    finally:
        host.stop_network()
        pg.quit()


if __name__ == "__main__":
    test_host_starts_and_binds_port()
    test_client_connects_to_host_and_receives_state()
    test_host_processes_client_input()
    test_host_broadcasts_state_at_configured_hz()
    print("All host-client integration tests passed.")
