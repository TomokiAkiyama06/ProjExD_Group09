"""起動時のモード選択メニューシーン。

引数なし起動時に表示し、Solo / Host / Client / Versus / Quit から選ばせる。
`run()` は選択結果の文字列（"solo" / "host" / "client" / "versus" / "quit"）を返す。
実際のゲーム起動は呼び出し側（main.py）が行う。

単体での動作確認はリポジトリルートで `python -m core.menu` を使う。
（`python core/menu.py` は相対 import が解決できず ImportError になるため不可。）

フォントは HUD と同じ `pg.font.SysFont(None, ...)` 方式。日本語フォント未配置だと
文字化けし得る（Issue #111）ため、選択肢ラベルは ASCII にしている。
"""

from __future__ import annotations

import pygame as pg

from .constants import COLOR_BG, COLOR_TEXT, FPS, SCREEN_HEIGHT, SCREEN_WIDTH

# 選択肢: (戻り値, 表示ラベル)
MENU_OPTIONS: list[tuple[str, str]] = [
    ("solo", "Solo  (1 PC / 2 players)"),
    ("host", "Host  (Player 1)"),
    ("client", "Client  (Player 2)"),
    ("versus", "Versus  (1 PC / 2 fields)"),
    ("quit", "Quit"),
]


class MenuScene:
    """モード選択メニュー。`run()` で選択結果の文字列を返す。

    描画に依存しない選択ロジック（`move_cursor` / `get_selected_value` /
    `set_index_from_mouse` / `handle_event`）は display なしでも動作するため、
    単体テストしやすい。
    """

    TITLE: str = "CO-EVOLUTION TOWER DEFENSE"
    TITLE_FONT_SIZE: int = 48
    OPTION_FONT_SIZE: int = 32
    HINT_FONT_SIZE: int = 20
    OPTION_GAP: int = 56
    COLOR_SELECTED: tuple[int, int, int] = (255, 220, 120)
    HINT: str = "[Up/Down] select   [Enter] decide   [Esc] quit"

    def __init__(
        self,
        screen: pg.Surface | None = None,
        options: list[tuple[str, str]] | None = None,
    ) -> None:
        if not pg.font.get_init():
            pg.font.init()
        self._screen: pg.Surface | None = screen
        self._clock: pg.time.Clock = pg.time.Clock()
        self._options: list[tuple[str, str]] = (
            list(options) if options is not None else list(MENU_OPTIONS)
        )
        self._index: int = 0
        self._title_font: pg.font.Font = pg.font.SysFont(None, self.TITLE_FONT_SIZE)
        self._option_font: pg.font.Font = pg.font.SysFont(None, self.OPTION_FONT_SIZE)
        self._hint_font: pg.font.Font = pg.font.SysFont(None, self.HINT_FONT_SIZE)

    # ----- selection logic（display 非依存） -----

    def get_index(self) -> int:
        """現在の選択インデックスを返す。"""
        return self._index

    def move_cursor(self, delta: int) -> None:
        """選択カーソルを delta だけ動かす（端で循環する）。"""
        self._index = (self._index + delta) % len(self._options)

    def get_selected_value(self) -> str:
        """現在の選択肢の戻り値文字列を返す。"""
        return self._options[self._index][0]

    def set_index_from_mouse(self, mouse_pos: tuple[int, int]) -> bool:
        """マウス座標が選択肢に重なればその index に移動する。

        Returns:
            いずれかの選択肢に重なった場合 True。
        """
        for i, rect in enumerate(self._option_rects()):
            if rect.collidepoint(mouse_pos):
                self._index = i
                return True
        return False

    def handle_event(self, event: pg.event.Event) -> str | None:
        """1 イベントを処理する。決定されたら選択値を返し、未決定なら None。"""
        if event.type == pg.QUIT:
            return "quit"
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_UP, pg.K_w):
                self.move_cursor(-1)
            elif event.key in (pg.K_DOWN, pg.K_s):
                self.move_cursor(1)
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                return self.get_selected_value()
            elif event.key == pg.K_ESCAPE:
                return "quit"
        elif event.type == pg.MOUSEMOTION:
            self.set_index_from_mouse(event.pos)
        elif (
            event.type == pg.MOUSEBUTTONDOWN
            and event.button == 1
            and self.set_index_from_mouse(event.pos)
        ):
            return self.get_selected_value()
        return None

    # ----- layout / draw -----

    def _option_rects(self) -> list[pg.Rect]:
        """各選択肢の描画矩形（中央揃え）を返す。"""
        rects: list[pg.Rect] = []
        start_y = SCREEN_HEIGHT // 2 - (len(self._options) - 1) * self.OPTION_GAP // 2
        for i, (_value, label) in enumerate(self._options):
            surf = self._option_font.render(label, True, COLOR_TEXT)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * self.OPTION_GAP))
            rects.append(rect)
        return rects

    def draw(self, screen: pg.Surface) -> None:
        """タイトル・選択肢・操作ヒントを描画する。"""
        screen.fill(COLOR_BG)
        title = self._title_font.render(self.TITLE, True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        rects = self._option_rects()
        for i, (_value, label) in enumerate(self._options):
            color = self.COLOR_SELECTED if i == self._index else COLOR_TEXT
            surf = self._option_font.render(label, True, color)
            screen.blit(surf, rects[i])

        hint = self._hint_font.render(self.HINT, True, COLOR_TEXT)
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 48)))

    # ----- run loop -----

    def run(self) -> str:
        """メニューを表示し、選択された値の文字列を返す。"""
        if self._screen is None:
            self._screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        while True:
            self._clock.tick(FPS)
            for event in pg.event.get():
                result = self.handle_event(event)
                if result is not None:
                    return result
            self.draw(self._screen)
            pg.display.flip()


if __name__ == "__main__":
    # 単体起動はリポジトリルートで `python -m core.menu`（直接 `python core/menu.py`
    # は相対 import が解決できないため不可）。
    pg.init()
    selected = MenuScene().run()
    pg.quit()
    print(f"selected: {selected}")
