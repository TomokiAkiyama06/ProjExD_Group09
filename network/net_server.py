"""UDP server wrapper."""

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
class NetServer:
    host: str = SERVER_HOST
    port: int = SERVER_PORT
    socket_obj: socket.socket = field(init=False)

    def __post_init__(self) -> None:
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_obj.bind((self.host, self.port))

    def receive(self, max_bytes: int = 4096) -> tuple[dict[str, Any], tuple[str, int]]:
        payload, address = self.socket_obj.recvfrom(max_bytes)
        return decode_message(payload), address

    def send(self, message: dict[str, Any], address: tuple[str, int]) -> None:
        self.socket_obj.sendto(encode_message(message), address)

    def close(self) -> None:
        self.socket_obj.close()
