"""プロジェクト共通のフォントローダ。"""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame as pg

FONT_DIR = Path(__file__).parent.parent / "assets" / "font"
FONT_DEFAULT = FONT_DIR / "NotoSansJP-Regular.ttf"


@cache
def get_font(size: int, path: Path = FONT_DEFAULT) -> pg.font.Font:
    """指定サイズのフォントを返す（同サイズはキャッシュ）。"""

    if not pg.font.get_init():
        pg.font.init()

    return pg.font.Font(str(path), size)