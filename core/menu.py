"""Start menu scene for choosing the launch mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pygame as pg

from .constants import COLOR_BG, COLOR_TEXT, FPS, SCREEN_HEIGHT, SCREEN_WIDTH

MenuMode = Literal["host", "client", "solo", "versus"]


@dataclass(frozen=True)
class MenuResult:
    """Selection made on the start menu."""

    mode: MenuMode
    ip: str = "127.0.0.1"


@dataclass(frozen=True)
class MenuItem:
    """Selectable menu item bounds."""

    mode: MenuMode
    label: str
    rect: pg.Rect


class MenuScene:
    """Mouse and keyboard operated mode selection menu."""

    MODES: tuple[tuple[MenuMode, str], ...] = (
        ("host", "Host"),
        ("client", "Client"),
        ("solo", "Solo"),
        ("versus", "Versus"),
    )

    def __init__(self, default_ip: str = "127.0.0.1") -> None:
        self._selected_index: int = 0
        self._ip_text: str = default_ip
        self._editing_ip: bool = False
        self._result: MenuResult | None = None
        self._running: bool = True
        self._items: list[MenuItem] = self._build_items()
        self._ip_rect: pg.Rect = pg.Rect(SCREEN_WIDTH // 2 - 170, 485, 340, 42)
        self._start_rect: pg.Rect = pg.Rect(SCREEN_WIDTH // 2 - 120, 550, 240, 48)
        self._font: pg.font.Font | None = None
        self._small_font: pg.font.Font | None = None
        self._title_font: pg.font.Font | None = None

    def get_result(self) -> MenuResult | None:
        """Return the selected mode, if the menu has finished."""
        return self._result

    def get_selected_mode(self) -> MenuMode:
        """Return the currently highlighted mode."""
        return self._items[self._selected_index].mode

    def get_ip_text(self) -> str:
        """Return the IP address currently typed in the field."""
        return self._ip_text

    def is_editing_ip(self) -> bool:
        """Return whether the IP field has keyboard focus."""
        return self._editing_ip

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle one pygame event."""
        if event.type == pg.QUIT:
            self._running = False
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(event.pos)
            return
        if event.type == pg.KEYDOWN:
            self._handle_key_down(event)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the menu scene."""
        self._ensure_fonts()
        assert self._font is not None
        assert self._small_font is not None
        assert self._title_font is not None

        screen.fill(COLOR_BG)
        self._draw_centered(screen, self._title_font, "ProjExD Defense", 115, COLOR_TEXT)
        self._draw_centered(screen, self._small_font, "Choose launch mode", 160, (170, 184, 205))

        mouse_pos = pg.mouse.get_pos()
        for index, item in enumerate(self._items):
            selected = index == self._selected_index
            hovered = item.rect.collidepoint(mouse_pos)
            self._draw_mode_button(screen, item, selected or hovered)

        self._draw_ip_input(screen)
        self._draw_start_button(screen)
        self._draw_centered(
            screen,
            self._small_font,
            "Arrow keys / Tab to move, Enter to start",
            SCREEN_HEIGHT - 50,
            (150, 160, 178),
        )

    def run(self) -> MenuResult | None:
        """Run the blocking menu loop."""
        pg.init()
        screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("ProjExD Defense - Start Menu")
        clock = pg.time.Clock()
        while self._running and self._result is None:
            clock.tick(FPS)
            for event in pg.event.get():
                self.handle_event(event)
            self.draw(screen)
            pg.display.flip()
        return self._result

    def _build_items(self) -> list[MenuItem]:
        """Build fixed menu button rectangles."""
        button_w = 210
        button_h = 58
        gap = 18
        total_w = button_w * 2 + gap
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        start_y = 230
        items: list[MenuItem] = []
        for index, (mode, label) in enumerate(self.MODES):
            col = index % 2
            row = index // 2
            rect = pg.Rect(
                start_x + col * (button_w + gap),
                start_y + row * (button_h + gap),
                button_w,
                button_h,
            )
            items.append(MenuItem(mode=mode, label=label, rect=rect))
        return items

    def _handle_mouse_down(self, pos: tuple[int, int]) -> None:
        """Handle left mouse clicks."""
        for index, item in enumerate(self._items):
            if item.rect.collidepoint(pos):
                self._selected_index = index
                self._editing_ip = item.mode == "client"
                return
        if self._ip_rect.collidepoint(pos):
            self._selected_index = self._mode_index("client")
            self._editing_ip = True
            return
        self._editing_ip = False
        if self._start_rect.collidepoint(pos):
            self._confirm_selection()

    def _handle_key_down(self, event: pg.event.Event) -> None:
        """Handle keyboard navigation and text entry."""
        if self._editing_ip and self._handle_ip_key(event):
            return
        if event.key in (pg.K_UP, pg.K_LEFT):
            self._move_selection(-1)
        elif event.key in (pg.K_DOWN, pg.K_RIGHT, pg.K_TAB):
            self._move_selection(1)
        elif event.key == pg.K_RETURN:
            if self.get_selected_mode() == "client" and not self._editing_ip:
                self._editing_ip = True
            else:
                self._confirm_selection()
        elif event.key == pg.K_ESCAPE:
            self._running = False

    def _handle_ip_key(self, event: pg.event.Event) -> bool:
        """Handle focused IP input keys."""
        if event.key == pg.K_BACKSPACE:
            self._ip_text = self._ip_text[:-1]
            return True
        if event.key == pg.K_RETURN:
            self._confirm_selection()
            return True
        if event.key == pg.K_ESCAPE:
            self._editing_ip = False
            return True
        if event.unicode and self._is_ip_character(event.unicode):
            self._ip_text = (self._ip_text + event.unicode)[:45]
            return True
        return False

    def _move_selection(self, step: int) -> None:
        """Move the highlighted menu item."""
        self._selected_index = (self._selected_index + step) % len(self._items)
        self._editing_ip = self.get_selected_mode() == "client"

    def _confirm_selection(self) -> None:
        """Finish the menu with the current selection."""
        mode = self.get_selected_mode()
        ip = self._ip_text.strip() or "127.0.0.1"
        self._result = MenuResult(mode=mode, ip=ip)
        self._running = False

    def _draw_mode_button(self, screen: pg.Surface, item: MenuItem, active: bool) -> None:
        """Draw a selectable mode button."""
        assert self._font is not None
        bg = (64, 88, 130) if active else (35, 42, 54)
        border = (145, 190, 255) if active else (92, 105, 126)
        pg.draw.rect(screen, bg, item.rect, border_radius=8)
        pg.draw.rect(screen, border, item.rect, width=2, border_radius=8)
        label = self._font.render(item.label, True, COLOR_TEXT)
        screen.blit(label, label.get_rect(center=item.rect.center))

    def _draw_ip_input(self, screen: pg.Surface) -> None:
        """Draw the client IP field."""
        assert self._font is not None
        assert self._small_font is not None
        label_color = COLOR_TEXT if self.get_selected_mode() == "client" else (130, 139, 154)
        label = self._small_font.render("Client host IP", True, label_color)
        screen.blit(label, (self._ip_rect.x, self._ip_rect.y - 28))
        bg = (28, 34, 44)
        border = (145, 190, 255) if self._editing_ip else (88, 98, 116)
        pg.draw.rect(screen, bg, self._ip_rect, border_radius=6)
        pg.draw.rect(screen, border, self._ip_rect, width=2, border_radius=6)
        text = self._font.render(self._ip_text, True, COLOR_TEXT)
        screen.blit(text, (self._ip_rect.x + 14, self._ip_rect.y + 8))

    def _draw_start_button(self, screen: pg.Surface) -> None:
        """Draw the launch button."""
        assert self._font is not None
        pg.draw.rect(screen, (82, 144, 118), self._start_rect, border_radius=8)
        pg.draw.rect(screen, (160, 230, 195), self._start_rect, width=2, border_radius=8)
        text = self._font.render("Start", True, COLOR_TEXT)
        screen.blit(text, text.get_rect(center=self._start_rect.center))

    def _draw_centered(
        self,
        screen: pg.Surface,
        font: pg.font.Font,
        text: str,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw text centered horizontally."""
        surface = font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(SCREEN_WIDTH // 2, y)))

    def _ensure_fonts(self) -> None:
        """Initialize font objects on first draw."""
        if not pg.font.get_init():
            pg.font.init()
        if self._font is None:
            self._font = pg.font.SysFont(None, 30)
            self._small_font = pg.font.SysFont(None, 22)
            self._title_font = pg.font.SysFont(None, 58)

    def _mode_index(self, mode: MenuMode) -> int:
        """Return the index of a menu mode."""
        for index, item in enumerate(self._items):
            if item.mode == mode:
                return index
        msg = f"unknown menu mode: {mode}"
        raise ValueError(msg)

    @staticmethod
    def _is_ip_character(value: str) -> bool:
        """Return True for characters accepted in an IP or host name."""
        return value.isascii() and (value.isalnum() or value in ".:-")


def run_menu(default_ip: str = "127.0.0.1") -> MenuResult | None:
    """Show the start menu and return the selected launch mode."""
    return MenuScene(default_ip=default_ip).run()
