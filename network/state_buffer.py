"""Interpolation buffer for networked state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StateBuffer:
    max_size: int = 30
    states: list[tuple[float, dict[str, Any]]] = field(default_factory=list)

    def push(self, timestamp: float, state: dict[str, Any]) -> None:
        self.states.append((timestamp, state))
        self.states.sort(key=lambda item: item[0])
        if len(self.states) > self.max_size:
            self.states = self.states[-self.max_size :]

    def latest(self) -> dict[str, Any] | None:
        if not self.states:
            return None
        return self.states[-1][1]
