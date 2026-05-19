"""JSON to bytes protocol helpers."""

from __future__ import annotations

import json
from typing import Any


def encode_message(message: dict[str, Any]) -> bytes:
    return json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def decode_message(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("network message must be a JSON object")
    return value
