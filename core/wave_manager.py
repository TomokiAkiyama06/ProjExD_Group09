"""Wave progression."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WaveManager:
    wave: int = 0
    enemies_remaining: int = 0

    def start_next_wave(self, enemy_count: int | None = None) -> int:
        self.wave += 1
        self.enemies_remaining = enemy_count if enemy_count is not None else 5 + self.wave * 2
        return self.enemies_remaining

    def mark_enemy_defeated(self) -> None:
        self.enemies_remaining = max(0, self.enemies_remaining - 1)

    @property
    def wave_complete(self) -> bool:
        return self.enemies_remaining == 0
