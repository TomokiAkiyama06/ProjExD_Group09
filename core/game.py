"""Base game loop shared by all modes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .constants import FPS


class Updatable(Protocol):
    def update(self, dt: float) -> None:
        ...


class Drawable(Protocol):
    def draw(self, surface: object) -> None:
        ...


@dataclass
class Game:
    """Small base class for game modes.

    Pygame-specific setup should be added by subclasses when rendering is ready.
    """

    fps: int = FPS
    running: bool = field(default=False, init=False)

    def handle_events(self) -> None:
        """Handle input and window events."""

    def update(self, dt: float) -> None:
        """Advance simulation state."""

    def draw(self) -> None:
        """Render the current frame."""

    def run(self) -> None:
        """Run a minimal placeholder loop.

        This intentionally avoids importing pygame until the real loop is added,
        so tests and module imports work before dependencies are installed.
        """
        self.running = True
        self.update(1.0 / self.fps)
        self.draw()
        self.running = False
