"""ネットワークプロトコル定義。

UDP上で送受信するメッセージのシリアライズ/デシリアライズと、
input/state/event/connect/ping の各メッセージ型を定義する。
"""

from __future__ import annotations

import json
from typing import Any, TypedDict

# ===== バイト変換 =====


def encode_message(message: dict[str, Any]) -> bytes:
    """Dict を UTF-8 bytes に変換する（区切り文字を詰めてサイズ削減）。"""
    return json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def decode_message(payload: bytes) -> dict[str, Any]:
    """Bytes を dict に変換する。失敗時は例外を投げる（既存挙動）。"""
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("network message must be a JSON object")
    return value


def serialize(msg: dict[str, Any]) -> bytes:
    """Dict を bytes に変換する（タスク #32 の安全版エイリアス）。"""
    return encode_message(msg)


def deserialize(data: bytes) -> dict[str, Any]:
    """Bytes を dict に変換する。

    不正なバイト列でも例外を投げず、空 dict を返す。受信スレッドが落ちないため
    の安全版。

    Returns:
        パース成功時はその dict、失敗時は空 dict。
    """
    try:
        value = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    return value


# ===== メッセージ型 =====
# UDP メッセージはすべて `type` フィールドで判別する。


# クライアント→ホスト：プレイヤー操作
class InputMessage(TypedDict):
    """input メッセージ。"""

    type: str
    seq: int
    player_id: int
    input: dict[str, Any]


# ホスト→クライアント：ゲーム状態
class StateMessage(TypedDict):
    """state メッセージ。"""

    type: str
    seq: int
    enemies: list[dict[str, Any]]
    towers: list[dict[str, Any]]
    players: list[dict[str, Any]]
    core_hp: int
    core_max_hp: int
    wave: int


# 双方向：重要イベント
class EventMessage(TypedDict):
    """event メッセージ。"""

    type: str
    seq: int
    event: str
    data: dict[str, Any]
    ack_required: bool


# ハンドシェイク
class ConnectMessage(TypedDict):
    """connect メッセージ（クライアント→ホスト）。"""

    type: str
    name: str


class ConnectOkMessage(TypedDict):
    """connect_ok メッセージ（ホスト→クライアント）。"""

    type: str
    player_id: int


# ハートビート
class PingMessage(TypedDict):
    """ping メッセージ。"""

    type: str
    seq: int


class PongMessage(TypedDict):
    """pong メッセージ。"""

    type: str
    seq: int


# ACK
class AckMessage(TypedDict):
    """ack メッセージ。"""

    type: str
    seq: int


# ===== メッセージファクトリ =====
# 既知の型のメッセージを安全に生成するためのヘルパ。


MSG_INPUT: str = "input"
MSG_STATE: str = "state"
MSG_EVENT: str = "event"
MSG_CONNECT: str = "connect"
MSG_CONNECT_OK: str = "connect_ok"
MSG_PING: str = "ping"
MSG_PONG: str = "pong"
MSG_ACK: str = "ack"


def make_input(seq: int, player_id: int, input_payload: dict[str, Any]) -> InputMessage:
    return {
        "type": MSG_INPUT,
        "seq": int(seq),
        "player_id": int(player_id),
        "input": dict(input_payload),
    }


def make_state(  # noqa: PLR0913 - state スキーマの全フィールドを引数化するため許容
    seq: int,
    *,
    enemies: list[dict[str, Any]] | None = None,
    towers: list[dict[str, Any]] | None = None,
    players: list[dict[str, Any]] | None = None,
    core_hp: int = 0,
    core_max_hp: int = 0,
    wave: int = 0,
) -> StateMessage:
    return {
        "type": MSG_STATE,
        "seq": int(seq),
        "enemies": list(enemies or []),
        "towers": list(towers or []),
        "players": list(players or []),
        "core_hp": int(core_hp),
        "core_max_hp": int(core_max_hp),
        "wave": int(wave),
    }


def make_event(
    seq: int,
    event_name: str,
    data: dict[str, Any] | None = None,
    *,
    ack_required: bool = True,
) -> EventMessage:
    return {
        "type": MSG_EVENT,
        "seq": int(seq),
        "event": str(event_name),
        "data": dict(data or {}),
        "ack_required": bool(ack_required),
    }


def make_connect(name: str) -> ConnectMessage:
    return {"type": MSG_CONNECT, "name": str(name)}


def make_connect_ok(player_id: int) -> ConnectOkMessage:
    return {"type": MSG_CONNECT_OK, "player_id": int(player_id)}


def make_ping(seq: int) -> PingMessage:
    return {"type": MSG_PING, "seq": int(seq)}


def make_pong(seq: int) -> PongMessage:
    return {"type": MSG_PONG, "seq": int(seq)}


def make_ack(seq: int) -> AckMessage:
    return {"type": MSG_ACK, "seq": int(seq)}
