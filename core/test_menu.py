"""Menu scene tests.

Run:
    python -m core.test_menu
"""

from __future__ import annotations

import os
from collections.abc import Callable

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

import core.menu
import main
from core.menu import MenuResult, MenuScene


def _key_event(key: int, unicode: str = "") -> pg.event.Event:
    """Build a KEYDOWN event for menu tests."""
    return pg.event.Event(pg.KEYDOWN, {"key": key, "unicode": unicode})


def _click_event(pos: tuple[int, int]) -> pg.event.Event:
    """Build a mouse click event for menu tests."""
    return pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


def test_keyboard_selects_solo() -> None:
    """Arrow navigation plus Enter selects solo mode."""
    menu = MenuScene()
    menu.handle_event(_key_event(pg.K_RIGHT))
    menu.handle_event(_key_event(pg.K_RIGHT))
    menu.handle_event(_key_event(pg.K_RETURN))

    assert menu.get_result() == MenuResult(mode="solo", ip="127.0.0.1")


def test_client_ip_input_accepts_keyboard_text() -> None:
    """Client mode allows IP editing before confirmation."""
    menu = MenuScene(default_ip="")
    menu.handle_event(_key_event(pg.K_RIGHT))
    assert menu.get_selected_mode() == "client"
    assert menu.is_editing_ip()

    for char in "192.168.0.8":
        menu.handle_event(_key_event(ord(char), char))
    menu.handle_event(_key_event(pg.K_RETURN))

    assert menu.get_result() == MenuResult(mode="client", ip="192.168.0.8")


def test_client_ip_input_supports_backspace_and_fallback() -> None:
    """Empty client IP falls back to localhost."""
    menu = MenuScene(default_ip="1")
    menu.handle_event(_key_event(pg.K_RIGHT))
    menu.handle_event(_key_event(pg.K_BACKSPACE))
    menu.handle_event(_key_event(pg.K_RETURN))

    assert menu.get_result() == MenuResult(mode="client", ip="127.0.0.1")


def test_mouse_click_selects_host_and_start() -> None:
    """Mouse can select a mode and start the game."""
    menu = MenuScene()
    host_center = menu._items[0].rect.center
    start_center = menu._start_rect.center

    menu.handle_event(_click_event(host_center))
    menu.handle_event(_click_event(start_center))

    assert menu.get_result() == MenuResult(mode="host", ip="127.0.0.1")


def test_main_uses_menu_when_no_mode_is_given() -> None:
    """No mode flag opens the menu and dispatches the selected result."""
    calls: list[tuple[str, object]] = []

    def fake_run_menu(default_ip: str = "127.0.0.1") -> MenuResult:
        calls.append(("menu", default_ip))
        return MenuResult(mode="client", ip="10.0.0.5")

    def fake_run_client(ip: str, port: int = 50000) -> None:
        calls.append(("client", (ip, port)))

    saved_run_menu = core.menu.run_menu
    saved_run_client = main.run_client
    try:
        core.menu.run_menu = fake_run_menu
        main.run_client = fake_run_client
        main.main([])
    finally:
        core.menu.run_menu = saved_run_menu
        main.run_client = saved_run_client

    assert calls == [("menu", "127.0.0.1"), ("client", ("10.0.0.5", 50000))]


def test_main_cli_modes_skip_menu() -> None:
    """Explicit CLI mode flags keep the old direct launch path."""
    calls: list[str] = []

    def record(name: str) -> Callable[..., None]:
        def inner(*_args: object, **_kwargs: object) -> None:
            calls.append(name)

        return inner

    saved_run_solo = main.run_solo
    saved_run_host = main.run_host
    saved_run_client = main.run_client
    saved_run_versus = main.run_versus
    try:
        main.run_solo = record("solo")
        main.run_host = record("host")
        main.run_client = record("client")
        main.run_versus = record("versus")

        main.main(["--solo"])
        main.main(["--host"])
        main.main(["--client", "--ip", "192.168.1.20"])
        main.main(["--versus"])
    finally:
        main.run_solo = saved_run_solo
        main.run_host = saved_run_host
        main.run_client = saved_run_client
        main.run_versus = saved_run_versus

    assert calls == ["solo", "host", "client", "versus"]


if __name__ == "__main__":
    pg.init()
    try:
        test_keyboard_selects_solo()
        test_client_ip_input_accepts_keyboard_text()
        test_client_ip_input_supports_backspace_and_fallback()
        test_mouse_click_selects_host_and_start()
        test_main_uses_menu_when_no_mode_is_given()
        test_main_cli_modes_skip_menu()
    finally:
        pg.quit()
    print("All menu tests passed.")
