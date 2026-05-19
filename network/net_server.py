"""UDP サーバ（権威サーバ型のホスト側）。

受信は専用スレッドで行い、結果を `queue.Queue` 経由でメインスレッドに渡す。
メインスレッドは毎フレーム `update(now)` を呼び、ACK 待ちイベントの再送と
ハートビートのタイムアウト検知を進める。

注意:
    - 受信ループは `select` 経由でブロックを区切り、`stop()` で安全に終了する。
    - 例外は受信スレッド・送信側ともに握り潰さずに `_errors` に積み、デバッグ可
      能にしている。
"""

from __future__ import annotations

import select
import socket
import threading
import time
from contextlib import suppress
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any

try:
    from ..core.constants import (
        NET_ACK_MAX_RETRIES,
        NET_ACK_RESEND_INTERVAL_SEC,
        NET_RECV_BUFFER_BYTES,
        NET_RECV_TIMEOUT_SEC,
        NET_TIMEOUT_SEC,
        SERVER_HOST,
        SERVER_PORT,
    )
except ImportError:
    from core.constants import (
        NET_ACK_MAX_RETRIES,
        NET_ACK_RESEND_INTERVAL_SEC,
        NET_RECV_BUFFER_BYTES,
        NET_RECV_TIMEOUT_SEC,
        NET_TIMEOUT_SEC,
        SERVER_HOST,
        SERVER_PORT,
    )

from .net_protocol import (
    MSG_ACK,
    MSG_CONNECT,
    MSG_EVENT,
    MSG_PING,
    decode_message,
    deserialize,
    encode_message,
    make_ack,
    make_connect_ok,
    make_event,
    make_pong,
    serialize,
)

Address = tuple[str, int]


@dataclass
class PlayerInfo:
    """接続中クライアントの情報。"""

    player_id: int
    name: str
    address: Address
    last_seen: float = 0.0
    last_seq: int = 0


@dataclass
class _PendingEvent:
    """ACK 待ちのイベント。"""

    seq: int
    payload: bytes
    targets: list[Address]
    retries: int = 0
    last_sent_at: float = 0.0


class NetServer:
    """UDP サーバ。"""

    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
    ) -> None:
        self._host: str = host
        self._port: int = port
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()

        self._inbox: Queue[tuple[Address, dict[str, Any]]] = Queue()
        self._errors: list[str] = []

        self._clients: dict[Address, PlayerInfo] = {}
        self._next_player_id: int = 1
        self._event_seq: int = 0
        self._pending: dict[int, _PendingEvent] = {}
        self._lock: threading.Lock = threading.Lock()

    # ----- lifecycle -----

    def start(self) -> None:
        """ソケットをバインドして受信スレッドを起動する。"""
        if self._sock is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))
        self._sock = sock
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """受信スレッドを停止しソケットを閉じる。"""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._sock is not None:
            with suppress(OSError):
                self._sock.close()
            self._sock = None

    # ----- accessors -----

    def get_clients(self) -> list[PlayerInfo]:
        with self._lock:
            return list(self._clients.values())

    def get_errors(self) -> list[str]:
        return list(self._errors)

    def get_bound_address(self) -> Address | None:
        if self._sock is None:
            return None
        try:
            return self._sock.getsockname()  # type: ignore[return-value]
        except OSError:
            return None

    # ----- recv -----

    def _recv_loop(self) -> None:
        sock = self._sock
        if sock is None:
            return
        while not self._stop_event.is_set():
            try:
                ready, _, _ = select.select([sock], [], [], NET_RECV_TIMEOUT_SEC)
            except (OSError, ValueError):
                break
            if not ready:
                continue
            try:
                payload, address = sock.recvfrom(NET_RECV_BUFFER_BYTES)
            except OSError as exc:
                self._errors.append(f"recvfrom failed: {exc!r}")
                continue
            self._handle_packet(payload, address)

    def _handle_packet(self, payload: bytes, address: Address) -> None:
        msg = deserialize(payload)
        if not msg:
            return
        msg_type = msg.get("type")

        if msg_type == MSG_CONNECT:
            self._handle_connect(address, msg)
            return
        if msg_type == MSG_PING:
            self._handle_ping(address, msg)
            return
        if msg_type == MSG_ACK:
            self._handle_ack(address, msg)
            return

        # 接続済みクライアントからの input / event はメインスレッドへ
        now = time.monotonic()
        with self._lock:
            client = self._clients.get(address)
            if client is not None:
                client.last_seen = now
        if msg_type == MSG_EVENT and bool(msg.get("ack_required", False)):
            self._send_raw(make_ack(int(msg.get("seq", 0))), address)

        self._inbox.put((address, msg))

    def _handle_connect(self, address: Address, msg: dict[str, Any]) -> None:
        now = time.monotonic()
        with self._lock:
            client = self._clients.get(address)
            if client is None:
                client = PlayerInfo(
                    player_id=self._next_player_id,
                    name=str(msg.get("name", "player")),
                    address=address,
                    last_seen=now,
                )
                self._clients[address] = client
                self._next_player_id += 1
            else:
                client.last_seen = now
            assigned_id = client.player_id

        # ack of connect (no event seq required, simple reply)
        self._send_raw(make_connect_ok(assigned_id), address)

    def _handle_ping(self, address: Address, msg: dict[str, Any]) -> None:
        now = time.monotonic()
        seq = int(msg.get("seq", 0))
        with self._lock:
            client = self._clients.get(address)
            if client is not None:
                client.last_seen = now
        self._send_raw(make_pong(seq), address)

    def _handle_ack(self, address: Address, msg: dict[str, Any]) -> None:
        seq = int(msg.get("seq", -1))
        with self._lock:
            pending = self._pending.get(seq)
            if pending is None:
                return
            if address in pending.targets:
                pending.targets.remove(address)
            if not pending.targets:
                self._pending.pop(seq, None)

    # ----- send -----

    def poll_messages(self) -> list[tuple[Address, dict[str, Any]]]:
        """受信キューを空にして取り出す。"""
        results: list[tuple[Address, dict[str, Any]]] = []
        while True:
            try:
                results.append(self._inbox.get_nowait())
            except Empty:
                break
        return results

    def _send_raw(self, msg: dict[str, Any], address: Address) -> bool:
        if self._sock is None:
            return False
        try:
            self._sock.sendto(serialize(msg), address)
        except OSError as exc:
            self._errors.append(f"sendto({address}) failed: {exc!r}")
            return False
        return True

    def broadcast(self, msg: dict[str, Any]) -> None:
        with self._lock:
            targets = [c.address for c in self._clients.values()]
        for addr in targets:
            self._send_raw(msg, addr)

    def send_state(self, state_msg: dict[str, Any]) -> None:
        """State メッセージを全クライアントに送信。

        頻度制御（20Hz）は呼び出し側のゲームループで行う想定。
        """
        if state_msg.get("type") != "state":
            self._errors.append(
                f"send_state: ignoring non-state message type={state_msg.get('type')!r}"
            )
            return
        self.broadcast(state_msg)

    def send_event(
        self,
        event_name: str,
        data: dict[str, Any] | None = None,
        *,
        ack_required: bool = True,
        target: Address | None = None,
    ) -> int:
        """重要イベントを送信。ack_required=True なら ACK 待ち→再送する。

        Returns:
            付与した seq 番号。
        """
        with self._lock:
            self._event_seq += 1
            seq = self._event_seq
        msg = make_event(seq, event_name, data, ack_required=ack_required)
        payload = encode_message(msg)
        with self._lock:
            targets = [c.address for c in self._clients.values()] if target is None else [target]
        now = time.monotonic()
        for addr in targets:
            self._send_raw(msg, addr)
        if ack_required and targets:
            with self._lock:
                self._pending[seq] = _PendingEvent(
                    seq=seq,
                    payload=payload,
                    targets=list(targets),
                    retries=0,
                    last_sent_at=now,
                )
        return seq

    # ----- main-loop tick -----

    def update(self, now: float | None = None) -> None:
        """メインスレッドから毎フレーム呼び出し、ACK 再送とタイムアウト処理を進める。"""
        if now is None:
            now = time.monotonic()
        self._resend_pending(now)
        self._evict_timeouts(now)

    def _resend_pending(self, now: float) -> None:
        with self._lock:
            due = [
                p
                for p in self._pending.values()
                if now - p.last_sent_at >= NET_ACK_RESEND_INTERVAL_SEC
            ]
        for pending in due:
            if pending.retries >= NET_ACK_MAX_RETRIES:
                self._errors.append(
                    f"event seq={pending.seq} reached max retries, giving up",
                )
                with self._lock:
                    self._pending.pop(pending.seq, None)
                continue
            for addr in pending.targets:
                if self._sock is None:
                    break
                try:
                    self._sock.sendto(pending.payload, addr)
                except OSError as exc:
                    self._errors.append(f"resend({addr}) failed: {exc!r}")
            with self._lock:
                ref = self._pending.get(pending.seq)
                if ref is not None:
                    ref.retries += 1
                    ref.last_sent_at = now

    def _evict_timeouts(self, now: float) -> None:
        with self._lock:
            dead = [
                addr for addr, c in self._clients.items() if now - c.last_seen > NET_TIMEOUT_SEC
            ]
            for addr in dead:
                self._clients.pop(addr, None)

    # ----- backward-compat thin API (used by existing tests / callers) -----

    def send(self, message: dict[str, Any], address: Address) -> None:
        """単発送信（ack なし）。"""
        self._send_raw(message, address)

    def close(self) -> None:
        """既存 API 互換のため stop() の別名。"""
        self.stop()

    def receive(self, max_bytes: int = NET_RECV_BUFFER_BYTES) -> tuple[dict[str, Any], Address]:
        """同期受信（既存 API 互換）。"""
        if self._sock is None:
            raise RuntimeError("server is not started")
        payload, address = self._sock.recvfrom(max_bytes)
        return decode_message(payload), address
