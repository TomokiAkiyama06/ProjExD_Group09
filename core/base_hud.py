"""Base HUD class."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BaseHud:
    messages: list[str] = field(default_factory=list)

    def push_message(self, message: str) -> None:
        self.messages.append(message)

    def draw(self, surface: object) -> None:
        _ = surface
