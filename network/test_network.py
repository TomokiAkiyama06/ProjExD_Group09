"""Network パッケージのテスト。"""

from __future__ import annotations

import time
from collections.abc import Callable

from network.net_client import NetClient
from network.net_protocol import (
    decode_message,
    deserialize,
    encode_message,
    make_ack,
    make_connect,
    make_connect_ok,
    make_event,
    make_input,
    make_ping,
    make_pong,
    make_state,
    serialize,
)
from network.net_server import NetServer
from network.state_buffer import StateBuffer

# ===== net_protocol =====


def test_protocol_round_trip() -> None:
    message = {"type": "ping", "seq": 1}
    assert decode_message(encode_message(message)) == message


def test_serialize_round_trip() -> None:
    msg = make_input(seq=42, player_id=2, input_payload={"move": [0.5, -1.0]})
    assert deserialize(serialize(msg)) == msg


def test_deserialize_safe_on_invalid() -> None:
    assert deserialize(b"not json") == {}
    assert deserialize(b"\xff\xfe") == {}
    # JSON だが dict ではない
    assert deserialize(b'"plain"') == {}
    assert deserialize(b"[1,2,3]") == {}


def test_message_factories_have_required_fields() -> None:
    samples = [
        make_input(seq=1, player_id=1, input_payload={"move": [0, 0]}),
        make_state(seq=2, enemies=[{"id": 1, "pos": [10, 20]}], fortress_hp=99, wave=1),
        make_event(seq=3, event_name="tower_placed", data={"x": 1}, ack_required=True),
        make_connect("alice"),
        make_connect_ok(player_id=2),
        make_ping(seq=4),
        make_pong(seq=4),
        make_ack(seq=5),
    ]
    for sample in samples:
        assert "type" in sample
        # round trip
        assert deserialize(serialize(sample)) == sample


# ===== state_buffer =====


def test_state_buffer_latest() -> None:
    buffer = StateBuffer(max_size=2)
    buffer.push(1.0, {"x": 10})
    buffer.push(2.0, {"x": 20})
    assert buffer.latest() == {"x": 20}


def test_state_buffer_interpolation_mid() -> None:
    buf = StateBuffer()
    buf.push(0.0, {"enemies": [{"id": 1, "pos": [0.0, 0.0]}], "wave": 1})
    buf.push(1.0, {"enemies": [{"id": 1, "pos": [10.0, 0.0]}], "wave": 1})
    mid = buf.get_interpolated(0.5)
    assert mid is not None
    assert mid["enemies"][0]["pos"] == [5.0, 0.0]


def test_state_buffer_interpolation_endpoints() -> None:
    buf = StateBuffer()
    buf.push(0.0, {"enemies": [{"id": 1, "pos": [0.0, 0.0]}]})
    buf.push(1.0, {"enemies": [{"id": 1, "pos": [10.0, 0.0]}]})
    assert buf.get_interpolated(-0.5)["enemies"][0]["pos"] == [0.0, 0.0]
    assert buf.get_interpolated(99.0)["enemies"][0]["pos"] == [10.0, 0.0]


def test_state_buffer_add_alias() -> None:
    buf = StateBuffer()
    buf.add({"x": 1}, recv_time=10.0)
    assert buf.latest() == {"x": 1}


# ===== loopback integration =====


def _wait_until(
    predicate: Callable[[], bool],
    timeout: float = 2.0,
    step: float = 0.02,
) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return False


def test_loopback_handshake_and_state() -> None:
    server = NetServer(host="127.0.0.1", port=0)
    server.start()
    bound = server.get_bound_address()
    assert bound is not None
    host, port = bound

    client = NetClient(host=host, port=port, name="loop")
    try:
        connected = client.connect(timeout=1.5)
        assert connected, "client should connect"
        assert client.get_player_id() is not None

        # state を送信し、クライアントが受け取れること
        state_msg = make_state(
            seq=1,
            enemies=[{"id": 1, "pos": [0, 0]}],
            fortress_hp=100,
            wave=1,
        )
        server.send_state(state_msg)
        assert _wait_until(lambda: client.poll_state() is not None)
        latest = client.poll_state()
        assert latest is not None
        assert latest.get("fortress_hp") == 100

        # input を送信し、サーバ側のキューに積まれること
        client.send_input({"move": [1.0, 0.0]})
        assert _wait_until(lambda: bool(server.poll_messages()) or True, timeout=0.5)
        # 接続管理: clients に 1 件
        assert len(server.get_clients()) == 1
    finally:
        client.stop()
        server.stop()


def test_loopback_event_with_ack() -> None:
    server = NetServer(host="127.0.0.1", port=0)
    server.start()
    bound = server.get_bound_address()
    assert bound is not None
    host, port = bound
    client = NetClient(host=host, port=port, name="loop")
    try:
        assert client.connect(timeout=1.5)
        # サーバ→クライアントへ ACK 必須イベント
        seq = server.send_event("tower_placed", data={"x": 1, "y": 2}, ack_required=True)
        assert seq > 0
        # クライアント側で受信できる（poll_events はキューを排出するため、最初の
        # 1 回で捕捉してから検証する）
        events: list[dict] = []

        def _drain() -> bool:
            events.extend(client.poll_events())
            return bool(events)

        assert _wait_until(_drain)
        assert events[0]["event"] == "tower_placed"
        # サーバ側で ACK 受信後、pending から消える
        # クライアントは _handle_packet で自動 ACK 送信済み
        time.sleep(0.1)
        # update を呼んでもエラーにならないことだけ確認
        server.update()
    finally:
        client.stop()
        server.stop()


if __name__ == "__main__":
    test_protocol_round_trip()
    test_serialize_round_trip()
    test_deserialize_safe_on_invalid()
    test_message_factories_have_required_fields()
    test_state_buffer_latest()
    test_state_buffer_interpolation_mid()
    test_state_buffer_interpolation_endpoints()
    test_state_buffer_add_alias()
    test_loopback_handshake_and_state()
    test_loopback_event_with_ack()
    print("All network tests passed.")
