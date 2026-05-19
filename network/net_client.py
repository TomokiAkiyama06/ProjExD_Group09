"""UDP client wrapper."""

from __future__ import annotations

import socket
from dataclasses import dataclass, field
from typing import Any

try:
    from ..core.constants import SERVER_HOST, SERVER_PORT
except ImportError:
    from core.constants import SERVER_HOST, SERVER_PORT

from .net_protocol import decode_message, encode_message


@dataclass
class NetClient:
    server_host: str = SERVER_HOST
    server_port: int = SERVER_PORT
    socket_obj: socket.socket = field(init=False)

    def __post_init__(self) -> None:
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: dict[str, Any]) -> None:
        self.socket_obj.sendto(encode_message(message), (self.server_host, self.server_port))

    def receive(self, max_bytes: int = 4096) -> dict[str, Any]:
        payload, _ = self.socket_obj.recvfrom(max_bytes)
        return decode_message(payload)

    def close(self) -> None:
        self.socket_obj.close()
