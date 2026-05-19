"""Entry point for ex5.

Keep this file short. Real game behavior should live in core modules.
"""

try:
    from .core.solo_game import SoloGame
except ImportError:
    from core.solo_game import SoloGame


def main() -> None:
    game = SoloGame()
    game.run()


if __name__ == "__main__":
    main()
