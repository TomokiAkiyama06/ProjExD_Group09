"""プロジェクト共通のフォントローダ。"""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

FONT_DIR = Path(__file__).parent.parent / "assets" / "font"
FONT_DEFAULT = FONT_DIR / "NotoSansJP-Regular.ttf"


@cache
def get_font(size: int, path: Path = FONT_DEFAULT):
    import pygame as pg

    try:
        if not pg.font.get_init():
            pg.font.init()

        return pg.font.Font(str(path), size)

    except Exception:
        return pg.font.SysFont(None, size)