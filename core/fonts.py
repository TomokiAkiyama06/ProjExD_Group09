"""プロジェクト共通のフォントローダ。"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import pygame as pg

FONT_DIR = Path(__file__).parent.parent / "assets" / "font"
FONT_DEFAULT = FONT_DIR / "NotoSansJP-Regular.otf"

@lru_cache(maxsize=None)
def get_font(size: int, path: Path = FONT_DEFAULT) -> pg.font.Font:
    """指定サイズのフォントを返す（同サイズはキャッシュ）。"""
    return pg.font.Font(str(path), size)