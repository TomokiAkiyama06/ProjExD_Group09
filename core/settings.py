"""User settings helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.constants import SETTINGS_FILE_NAME, SETTINGS_KEY_TUTORIAL_SEEN


def get_settings_path() -> Path:
    """設定ファイルの保存先を返す。"""
    return Path(SETTINGS_FILE_NAME)


def load_settings(path: Path | None = None) -> dict[str, object]:
    """設定ファイルを読み込む。

    ファイルが無い場合や JSON が壊れている場合は空の設定として扱う。
    """
    settings_path = path or get_settings_path()
    try:
        data: Any = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return dict(data)


def save_settings(settings: dict[str, object], path: Path | None = None) -> None:
    """設定ファイルへ保存する。保存できない場合は何もしない。"""
    settings_path = path or get_settings_path()
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(settings, ensure_ascii=False, indent=2)
        settings_path.write_text(f"{text}\n", encoding="utf-8")
    except OSError:
        return


def get_tutorial_seen(path: Path | None = None) -> bool:
    """チュートリアル表示済みフラグを返す。"""
    settings = load_settings(path)
    return bool(settings.get(SETTINGS_KEY_TUTORIAL_SEEN, False))


def set_tutorial_seen(value: bool, path: Path | None = None) -> None:
    """チュートリアル表示済みフラグを保存する。"""
    settings = load_settings(path)
    settings[SETTINGS_KEY_TUTORIAL_SEEN] = bool(value)
    save_settings(settings, path)
