"""Settings helper tests.

実行方法:
    python -m core.test_settings
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from core.constants import SETTINGS_KEY_TUTORIAL_SEEN
from core.settings import get_tutorial_seen, load_settings, save_settings, set_tutorial_seen


def test_missing_settings_returns_false() -> None:
    """設定ファイルが無い場合は初回扱いにする。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        assert not get_tutorial_seen(path)


def test_broken_settings_returns_false() -> None:
    """壊れた JSON はクラッシュせず初回扱いにする。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        path.write_text("{broken", encoding="utf-8")
        assert not get_tutorial_seen(path)


def test_non_dict_settings_returns_empty() -> None:
    """Dict 以外の JSON は空設定として扱う。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        path.write_text("[]", encoding="utf-8")
        assert load_settings(path) == {}


def test_save_and_load_settings() -> None:
    """設定を書き込んで読み戻せる。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        save_settings({SETTINGS_KEY_TUTORIAL_SEEN: True}, path)
        assert get_tutorial_seen(path)


def test_set_tutorial_seen() -> None:
    """チュートリアル表示済みフラグを保存できる。"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        set_tutorial_seen(True, path)
        assert get_tutorial_seen(path)


def test_save_settings_ignores_write_failure() -> None:
    """保存できない場所でも設定保存は例外にしない。"""
    with tempfile.TemporaryDirectory() as tmp:
        parent_file = Path(tmp) / "parent_file"
        parent_file.write_text("not a directory", encoding="utf-8")
        path = parent_file / "settings.json"
        save_settings({SETTINGS_KEY_TUTORIAL_SEEN: True}, path)
        set_tutorial_seen(True, path)


if __name__ == "__main__":
    test_missing_settings_returns_false()
    test_broken_settings_returns_false()
    test_non_dict_settings_returns_empty()
    test_save_and_load_settings()
    test_set_tutorial_seen()
    print("All tests passed.")
