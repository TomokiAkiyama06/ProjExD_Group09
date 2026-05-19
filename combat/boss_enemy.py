"""Boss enemy."""

from __future__ import annotations

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy


class BossEnemy(BaseEnemy):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(hp=180, speed=35.0, reward=10, **kwargs)
