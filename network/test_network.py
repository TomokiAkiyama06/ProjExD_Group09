"""Tests for network helpers."""

from __future__ import annotations

from network.net_protocol import decode_message, encode_message
from network.state_buffer import StateBuffer


def test_protocol_round_trip() -> None:
    message = {"type": "ping", "seq": 1}
    assert decode_message(encode_message(message)) == message


def test_state_buffer_latest() -> None:
    buffer = StateBuffer(max_size=2)
    buffer.push(1.0, {"x": 10})
    buffer.push(2.0, {"x": 20})
    assert buffer.latest() == {"x": 20}
