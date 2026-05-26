"""Tutorial overlay drawing for first-time players."""

from __future__ import annotations

import pygame as pg

try:
    from ..core.constants import (
        COLOR_TEXT,
        HUD_PANEL_BG,
        HUD_PANEL_BORDER,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
    )
except ImportError:
    from core.constants import (
        COLOR_TEXT,
        HUD_PANEL_BG,
        HUD_PANEL_BORDER,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
    )


class TutorialOverlay:
    """操作説明をゲーム画面に重ねて描画するオーバーレイ。"""

    PANEL_WIDTH: int = 760
    PANEL_PADDING: int = 24
    TITLE_FONT_SIZE: int = 34
    SECTION_FONT_SIZE: int = 24
    BODY_FONT_SIZE: int = 20
    LINE_HEIGHT: int = 28
    CLOSE_BUTTON_SIZE: int = 34

    def __init__(self) -> None:
        if not pg.font.get_init():
            pg.font.init()
        self._title_font: pg.font.Font = pg.font.SysFont(None, self.TITLE_FONT_SIZE)
        self._section_font: pg.font.Font = pg.font.SysFont(None, self.SECTION_FONT_SIZE)
        self._body_font: pg.font.Font = pg.font.SysFont(None, self.BODY_FONT_SIZE)
        self._visible: bool = True
        self._close_rect: pg.Rect = pg.Rect(0, 0, self.CLOSE_BUTTON_SIZE, self.CLOSE_BUTTON_SIZE)

    def is_visible(self) -> bool:
        """表示中なら True を返す。"""
        return self._visible

    def show(self) -> None:
        """オーバーレイを表示する。"""
        self._visible = True

    def hide(self) -> None:
        """オーバーレイを非表示にする。"""
        self._visible = False

    def handle_event(self, event: pg.event.Event) -> bool:
        """閉じる操作を処理し、閉じた場合は True を返す。"""
        if not self._visible:
            return False
        if event.type == pg.KEYDOWN:
            self.hide()
            return True
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.hide()
            return True
        return False

    def draw(self, screen: pg.Surface) -> None:
        """半透明背景と操作説明を描画する。"""
        if not self._visible:
            return
        self._draw_backdrop(screen)
        panel_rect = self._build_panel_rect()
        self._close_rect = pg.Rect(
            panel_rect.right - self.PANEL_PADDING - self.CLOSE_BUTTON_SIZE,
            panel_rect.y + self.PANEL_PADDING,
            self.CLOSE_BUTTON_SIZE,
            self.CLOSE_BUTTON_SIZE,
        )
        pg.draw.rect(screen, HUD_PANEL_BG, panel_rect, border_radius=8)
        pg.draw.rect(screen, HUD_PANEL_BORDER, panel_rect, width=2, border_radius=8)
        self._draw_contents(screen, panel_rect)
        self._draw_close_button(screen)

    def _draw_backdrop(self, screen: pg.Surface) -> None:
        """ゲーム画面を暗くする半透明背景を描画する。"""
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

    def _build_panel_rect(self) -> pg.Rect:
        """中央に配置する説明パネルの矩形を返す。"""
        height = 500
        return pg.Rect(
            (SCREEN_WIDTH - self.PANEL_WIDTH) // 2,
            (SCREEN_HEIGHT - height) // 2,
            self.PANEL_WIDTH,
            height,
        )

    def _draw_contents(self, screen: pg.Surface, panel_rect: pg.Rect) -> None:
        """説明文をパネル内に描画する。"""
        x = panel_rect.x + self.PANEL_PADDING
        y = panel_rect.y + self.PANEL_PADDING
        title = self._title_font.render("Controls", True, COLOR_TEXT)
        screen.blit(title, (x, y))
        y += 52

        sections = [
            (
                "Player 1 / Builder",
                [
                    "1-4: select tower type",
                    "Left click: place tower",
                    "Right click: select tower",
                    "Space: request next wave",
                ],
            ),
            (
                "Player 2 / Fighter",
                [
                    "WASD: move",
                    "Shift: dash",
                    "J: attack",
                    "K: use skill",
                    "L: repair nearby tower",
                ],
            ),
            (
                "Weapons / Skills",
                [
                    "Q / E: switch weapon",
                    "5 / 6: switch skill",
                ],
            ),
        ]

        for heading, lines in sections:
            heading_surface = self._section_font.render(heading, True, COLOR_TEXT)
            screen.blit(heading_surface, (x, y))
            y += 30
            for line in lines:
                body_surface = self._body_font.render(line, True, COLOR_TEXT)
                screen.blit(body_surface, (x + 18, y))
                y += self.LINE_HEIGHT
            y += 12

    def _draw_close_button(self, screen: pg.Surface) -> None:
        """閉じるボタンを描画する。"""
        pg.draw.rect(screen, HUD_PANEL_BORDER, self._close_rect, border_radius=4)
        label = self._body_font.render("X", True, COLOR_TEXT)
        screen.blit(label, label.get_rect(center=self._close_rect.center))
