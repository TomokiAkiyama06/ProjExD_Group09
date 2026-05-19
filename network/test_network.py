"""Network パッケージのテスト。"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

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
from network.net_server import NetServer, PlayerInfo, _PendingEvent
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
        make_state(seq=2, enemies=[{"id": 1, "pos": [10, 20]}], core_hp=99, core_max_hp=100, wave=1),
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
            core_hp=100,
            core_max_hp=1000,
            wave=1,
        )
        server.send_state(state_msg)
        assert _wait_until(lambda: client.poll_state() is not None)
        latest = client.poll_state()
        assert latest is not None
        assert latest.get("core_hp") == 100

        # input を送信し、サーバ側のキューに積まれること
        client.send_input({"move": [1.0, 0.0]})
        received_inputs: list[dict] = []

        def _server_received_input() -> bool:
            received_inputs.extend(msg for _, msg in server.poll_messages())
            return any(msg.get("type") == "input" for msg in received_inputs)

        assert _wait_until(_server_received_input, timeout=0.5)
        assert received_inputs[0]["input"] == {"move": [1.0, 0.0]}
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


def test_loopback_client_event_receives_ack() -> None:
    server = NetServer(host="127.0.0.1", port=0)
    server.start()
    bound = server.get_bound_address()
    assert bound is not None
    host, port = bound
    client = NetClient(host=host, port=port, name="loop")
    try:
        assert client.connect(timeout=1.5)
        seq = client.send_event("send_enemy", data={"kind": "fast"}, ack_required=True)
        assert seq in client._pending

        received: list[dict] = []

        def _server_received_event() -> bool:
            received.extend(msg for _, msg in server.poll_messages())
            return bool(received)

        assert _wait_until(_server_received_event)
        assert received[0]["event"] == "send_enemy"
        assert _wait_until(lambda: seq not in client._pending)
    finally:
        client.stop()
        server.stop()


def test_server_ack_tracks_pending_targets_per_client() -> None:
    server = NetServer()
    addr1 = ("127.0.0.1", 10001)
    addr2 = ("127.0.0.1", 10002)
    server._pending[7] = _PendingEvent(
        seq=7,
        payload=b"{}",
        targets=[addr1, addr2],
    )

    server._handle_ack(addr1, make_ack(7))
    assert 7 in server._pending
    assert server._pending[7].targets == [addr2]

    server._handle_ack(addr2, make_ack(7))
    assert 7 not in server._pending


def test_server_rejects_messages_from_unconnected_address() -> None:
    server = NetServer()
    addr = ("127.0.0.1", 10001)

    server._handle_packet(serialize(make_input(1, 1, {"move": [1, 0]})), addr)
    assert server.poll_messages() == []


def test_server_discards_stale_input_seq() -> None:
    server = NetServer()
    addr = ("127.0.0.1", 10001)
    server._clients[addr] = PlayerInfo(player_id=1, name="p1", address=addr)

    server._handle_packet(serialize(make_input(2, 1, {"move": [2, 0]})), addr)
    server._handle_packet(serialize(make_input(1, 1, {"move": [1, 0]})), addr)

    messages = server.poll_messages()
    assert len(messages) == 1
    assert messages[0][1]["seq"] == 2


def test_server_registers_pending_before_sending_event() -> None:
    server = NetServer()
    addr = ("127.0.0.1", 10001)
    server._clients[addr] = PlayerInfo(player_id=1, name="p1", address=addr)

    def _ack_immediately(msg: dict, address: tuple[str, int]) -> bool:
        seq = int(msg["seq"])
        assert seq in server._pending
        server._handle_ack(address, make_ack(seq))
        return True

    server._send_raw = _ack_immediately  # type: ignore[method-assign]
    seq = server.send_event("tower_placed", ack_required=True)
    assert seq not in server._pending


def test_client_registers_pending_before_sending_event() -> None:
    client = NetClient()
    sent: list[int] = []

    def _ack_immediately(msg: dict[str, Any]) -> bool:
        seq = int(msg["seq"])
        assert seq in client._pending
        client._handle_packet(serialize(make_ack(seq)))
        sent.append(seq)
        return True

    client._send_raw = _ack_immediately  # type: ignore[method-assign]
    seq = client.send_event("send_enemy", ack_required=True)

    assert sent == [seq]
    assert seq not in client._pending


def test_server_deduplicates_retried_client_events_but_acks_each_time() -> None:
    server = NetServer()
    addr = ("127.0.0.1", 10001)
    server._clients[addr] = PlayerInfo(player_id=1, name="p1", address=addr)
    acks: list[tuple[tuple[str, int], dict[str, Any]]] = []

    def _capture_ack(msg: dict[str, Any], address: tuple[str, int]) -> bool:
        acks.append((address, msg))
        return True

    server._send_raw = _capture_ack  # type: ignore[method-assign]
    payload = serialize(make_event(4, "send_enemy", {"kind": "fast"}, ack_required=True))

    server._handle_packet(payload, addr)
    server._handle_packet(payload, addr)

    messages = server.poll_messages()
    assert len(messages) == 1
    assert messages[0][1]["event"] == "send_enemy"
    assert acks == [(addr, make_ack(4)), (addr, make_ack(4))]


def test_client_deduplicates_retried_server_events_but_acks_each_time() -> None:
    client = NetClient()
    acks: list[dict[str, Any]] = []

    def _capture_ack(msg: dict[str, Any]) -> bool:
        acks.append(msg)
        return True

    client._send_raw = _capture_ack  # type: ignore[method-assign]
    payload = serialize(make_event(5, "tower_placed", {"x": 1}, ack_required=True))

    client._handle_packet(payload)
    client._handle_packet(payload)

    events = client.poll_events()
    assert len(events) == 1
    assert events[0]["event"] == "tower_placed"
    assert acks == [make_ack(5), make_ack(5)]


def test_server_ignores_bad_ping_seq_without_crashing() -> None:
    server = NetServer()
    addr = ("127.0.0.1", 10001)
    sent: list[tuple[tuple[str, int], dict[str, Any]]] = []

    def _capture_send(msg: dict[str, Any], address: tuple[str, int]) -> bool:
        sent.append((address, msg))
        return True

    server._send_raw = _capture_send  # type: ignore[method-assign]
    server._handle_packet(serialize({"type": "ping", "seq": "bad"}), addr)

    assert sent == []


def test_client_resets_lost_connection_on_connect_ok() -> None:
    client = NetClient()
    client._lost_connection = True

    client._handle_packet(serialize(make_connect_ok(2)))

    assert client.is_connected()
    assert not client.has_lost_connection()


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
    test_loopback_client_event_receives_ack()
    test_server_ack_tracks_pending_targets_per_client()
    test_server_rejects_messages_from_unconnected_address()
    test_server_discards_stale_input_seq()
    test_server_registers_pending_before_sending_event()
    test_client_registers_pending_before_sending_event()
    test_server_deduplicates_retried_client_events_but_acks_each_time()
    test_client_deduplicates_retried_server_events_but_acks_each_time()
    test_server_ignores_bad_ping_seq_without_crashing()
    test_client_resets_lost_connection_on_connect_ok()
    print("All network tests passed.")
