"""BGM and sound effect manager."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SoundManager:
    enabled: bool = True
    loaded: dict[str, object] = field(default_factory=dict)

    def load(self, name: str, sound: object) -> None:
        self.loaded[name] = sound

    def play(self, name: str) -> bool:
        return self.enabled and name in self.loaded
