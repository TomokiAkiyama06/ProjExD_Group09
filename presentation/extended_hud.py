"""Extended HUD."""

from __future__ import annotations

try:
    from ..core.base_hud import BaseHud
except ImportError:
    from core.base_hud import BaseHud


class ExtendedHud(BaseHud):
    def set_status(self, wave: int, money: int) -> None:
        self.messages = [f"wave={wave}", f"money={money}"]
