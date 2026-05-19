"""Special enemy variants."""

from __future__ import annotations

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy


class SpecialEnemy(BaseEnemy):
    special_type = "runner"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(hp=20, speed=130.0, reward=2, **kwargs)
