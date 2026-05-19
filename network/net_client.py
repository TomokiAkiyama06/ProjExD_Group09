"""UDP クライアント（描画のみ担うクライアント側）。

受信は専用スレッドで行い、最新 state は内部バッファに、event は別キューに積む。
メインスレッドからは `poll_state()` / `poll_events()` を呼ぶ。`update(now)` で
ハートビートの送信、サーバ無応答検知、ACK 待ちイベントの再送を進める。
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
        NET_PING_INTERVAL_SEC,
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
        NET_PING_INTERVAL_SEC,
        NET_RECV_BUFFER_BYTES,
        NET_RECV_TIMEOUT_SEC,
        NET_TIMEOUT_SEC,
        SERVER_HOST,
        SERVER_PORT,
    )

from .net_protocol import (
    MSG_ACK,
    MSG_CONNECT_OK,
    MSG_EVENT,
    MSG_PONG,
    MSG_STATE,
    decode_message,
    deserialize,
    encode_message,
    make_ack,
    make_connect,
    make_event,
    make_input,
    make_ping,
    serialize,
)

Address = tuple[str, int]


def _to_int(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass
class _PendingEvent:
    """ACK 待ちイベント。"""

    seq: int
    payload: bytes
    retries: int = 0
    last_sent_at: float = 0.0


class NetClient:
    """UDP クライアント。"""

    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        name: str = "player",
    ) -> None:
        self._host: str = host
        self._port: int = port
        self._name: str = name
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()

        self._connected: threading.Event = threading.Event()
        self._player_id: int | None = None
        self._last_seen: float = 0.0
        self._lost_connection: bool = False

        self._ping_seq: int = 0
        self._input_seq: int = 0
        self._event_seq: int = 0
        self._pending: dict[int, _PendingEvent] = {}
        self._received_event_seqs: set[int] = set()

        self._latest_state: dict[str, Any] | None = None
        self._latest_state_time: float = 0.0
        self._latest_state_seq: int = -1
        self._events_inbox: Queue[dict[str, Any]] = Queue()
        self._errors: list[str] = []

        self._last_ping_at: float = 0.0

        self._lock: threading.Lock = threading.Lock()

    # ----- lifecycle -----

    def start(self) -> None:
        """ソケットを準備して受信スレッドを起動する（送信はメインスレッド）。"""
        if self._sock is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 0))  # 任意ポート
        self._sock = sock
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._sock is not None:
            with suppress(OSError):
                self._sock.close()
            self._sock = None
        self._connected.clear()
        self._player_id = None

    # ----- public protocol -----

    def connect(self, timeout: float = 3.0) -> bool:
        """ホストに connect を送り connect_ok を待つ。

        Returns:
            タイムアウト内に player_id を受け取れたら True。
        """
        if self._sock is None:
            self.start()
        self._connected.clear()
        self._lost_connection = False
        msg = make_connect(self._name)
        self._send_raw(msg)
        ok = self._connected.wait(timeout=timeout)
        if ok:
            self._last_seen = time.monotonic()
            self._last_ping_at = self._last_seen
        return ok

    def send_input(self, input_payload: dict[str, Any]) -> None:
        """30Hz で呼ばれる想定の操作送信。"""
        if not self._connected.is_set() or self._player_id is None:
            return
        with self._lock:
            self._input_seq += 1
            seq = self._input_seq
        self._send_raw(make_input(seq, self._player_id, input_payload))

    def send_event(
        self,
        event_name: str,
        data: dict[str, Any] | None = None,
        *,
        ack_required: bool = True,
    ) -> int:
        """ホストにイベントを送信。ack_required=True なら ACK 待ち→再送する。"""
        with self._lock:
            self._event_seq += 1
            seq = self._event_seq
        msg = make_event(seq, event_name, data, ack_required=ack_required)
        payload = encode_message(msg)
        if ack_required:
            now = time.monotonic()
            with self._lock:
                self._pending[seq] = _PendingEvent(
                    seq=seq,
                    payload=payload,
                    retries=0,
                    last_sent_at=now,
                )
        sent = self._send_raw(msg)
        if ack_required and not sent:
            with self._lock:
                self._pending.pop(seq, None)
        return seq

    def poll_state(self) -> dict[str, Any] | None:
        """最新の state を返す（補間が必要ならクライアント側で StateBuffer に push）。"""
        with self._lock:
            return self._latest_state

    def poll_events(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        while True:
            try:
                out.append(self._events_inbox.get_nowait())
            except Empty:
                break
        return out

    # ----- status -----

    def is_connected(self) -> bool:
        return self._connected.is_set() and not self._lost_connection

    def get_player_id(self) -> int | None:
        return self._player_id

    def has_lost_connection(self) -> bool:
        return self._lost_connection

    def get_errors(self) -> list[str]:
        return list(self._errors)

    # ----- per-frame -----

    def update(self, now: float | None = None) -> None:
        if now is None:
            now = time.monotonic()
        self._maybe_send_ping(now)
        self._check_server_timeout(now)
        self._resend_pending(now)

    def _maybe_send_ping(self, now: float) -> None:
        if not self._connected.is_set():
            return
        if now - self._last_ping_at < NET_PING_INTERVAL_SEC:
            return
        with self._lock:
            self._ping_seq += 1
            seq = self._ping_seq
        self._send_raw(make_ping(seq))
        self._last_ping_at = now

    def _check_server_timeout(self, now: float) -> None:
        if not self._connected.is_set():
            return
        if now - self._last_seen > NET_TIMEOUT_SEC:
            self._lost_connection = True

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
            if self._sock is None:
                break
            try:
                self._sock.sendto(pending.payload, (self._host, self._port))
            except OSError as exc:
                self._errors.append(f"resend failed: {exc!r}")
            with self._lock:
                ref = self._pending.get(pending.seq)
                if ref is not None:
                    ref.retries += 1
                    ref.last_sent_at = now

    # ----- recv -----

    def _send_raw(self, msg: dict[str, Any]) -> bool:
        if self._sock is None:
            return False
        try:
            self._sock.sendto(serialize(msg), (self._host, self._port))
        except OSError as exc:
            self._errors.append(f"send failed: {exc!r}")
            return False
        return True

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
            if address != (self._host, self._port):
                continue
            self._handle_packet(payload)

    def _handle_packet(self, payload: bytes) -> None:  # noqa: PLR0911, PLR0912 - 受信メッセージ種別ごとの early return で見通しを保つ
        msg = deserialize(payload)
        if not msg:
            return
        msg_type = msg.get("type")
        now = time.monotonic()
        self._last_seen = now

        if msg_type == MSG_CONNECT_OK:
            player_id = _to_int(msg.get("player_id", 0))
            if player_id is None or player_id <= 0:
                return
            self._player_id = player_id
            self._lost_connection = False
            self._connected.set()
            return
        if msg_type == MSG_STATE:
            seq = _to_int(msg.get("seq", 0))
            if seq is None:
                return
            with self._lock:
                # 古い seq は破棄（パケット並べ替え対策）
                if seq < self._latest_state_seq:
                    return
                self._latest_state = msg
                self._latest_state_seq = seq
                self._latest_state_time = now
            return
        if msg_type == MSG_PONG:
            return  # last_seen 更新済み
        if msg_type == MSG_EVENT:
            seq = _to_int(msg.get("seq", -1))
            if seq is None:
                return
            ack_required = bool(msg.get("ack_required", False))
            if ack_required:
                self._send_raw(make_ack(seq))
                with self._lock:
                    if seq in self._received_event_seqs:
                        return
                    self._received_event_seqs.add(seq)
            self._events_inbox.put(msg)
            return
        if msg_type == MSG_ACK:
            seq = _to_int(msg.get("seq", -1))
            if seq is None:
                return
            with self._lock:
                self._pending.pop(seq, None)
            return

    # ----- backward-compat thin API -----

    def send(self, message: dict[str, Any]) -> None:
        """単発送信（既存 API 互換）。"""
        self._send_raw(message)

    def receive(self, max_bytes: int = NET_RECV_BUFFER_BYTES) -> dict[str, Any]:
        """同期受信（既存 API 互換）。"""
        if self._sock is None:
            raise RuntimeError("client is not started")
        payload, _ = self._sock.recvfrom(max_bytes)
        return decode_message(payload)

    def close(self) -> None:
        """既存 API 互換の停止呼び出し。"""
        self.stop()
