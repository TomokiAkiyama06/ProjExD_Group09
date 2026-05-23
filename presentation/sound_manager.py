"""BGM・SE 管理マネージャ。

`core.world.SoundSink` Protocol を実装し、`SoloGame` / `VersusGame` 等から
注入される。pg.mixer の初期化に失敗した場合や音源ファイルが見つからない
場合でも例外を投げず、全 `play_*` を no-op として処理する（CI 環境や
音源未配置の段階でゲームが落ちないようにするため）。

音源は `assets/sound/<name>.wav` または `<name>.ogg` を想定。
`auto_load_from_dir()` でディレクトリ内を走査し名前 → Sound オブジェクトの
キャッシュ `_se_cache` を構築する。
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import ClassVar

import pygame as pg

try:
    from ..core.constants import (
        SOUND_ASSET_DIR,
        SOUND_DEFAULT_BGM_VOLUME,
        SOUND_DEFAULT_SE_VOLUME,
        SOUND_MIXER_CHANNELS,
        SOUND_MIXER_FREQUENCY,
    )
except ImportError:
    from core.constants import (
        SOUND_ASSET_DIR,
        SOUND_DEFAULT_BGM_VOLUME,
        SOUND_DEFAULT_SE_VOLUME,
        SOUND_MIXER_CHANNELS,
        SOUND_MIXER_FREQUENCY,
    )


class SoundManager:
    """BGM・SE 再生を統一管理する。"""

    SUPPORTED_SE_EXTS: ClassVar[tuple[str, ...]] = (".wav", ".ogg")
    SUPPORTED_BGM_EXTS: ClassVar[tuple[str, ...]] = (".ogg", ".wav", ".mp3")

    def __init__(
        self,
        asset_dir: str | Path = SOUND_ASSET_DIR,
        se_volume: float = SOUND_DEFAULT_SE_VOLUME,
        bgm_volume: float = SOUND_DEFAULT_BGM_VOLUME,
        auto_load: bool = True,
    ) -> None:
        """SoundManager を初期化し、必要なら asset_dir 配下の SE を自動ロードする。

        Args:
            asset_dir: SE/BGM 検索先のディレクトリ。
            se_volume: SE 初期音量（0.0〜1.0 にクランプ）。
            bgm_volume: BGM 初期音量（0.0〜1.0 にクランプ）。
            auto_load: True なら ``__init__`` 末尾で ``auto_load_from_dir`` を
                呼び ``asset_dir`` 配下の SE をキャッシュする。テスト等で
                明示制御したい場合に False を指定する。
        """
        self._asset_dir: Path = Path(asset_dir)
        self._se_volume: float = max(0.0, min(1.0, float(se_volume)))
        self._bgm_volume: float = max(0.0, min(1.0, float(bgm_volume)))
        self._se_cache: dict[str, pg.mixer.Sound] = {}
        self._current_bgm: str | None = None
        self._enabled: bool = self._init_mixer()
        if auto_load:
            self.auto_load_from_dir()

    # ----- lifecycle -----

    def _init_mixer(self) -> bool:
        """pg.mixer.init を試行する。失敗時は静かに False を返す。"""
        try:
            pg.mixer.init(
                frequency=SOUND_MIXER_FREQUENCY,
                channels=SOUND_MIXER_CHANNELS,
            )
        except (pg.error, OSError):
            return False
        with suppress(pg.error):
            pg.mixer.music.set_volume(self._bgm_volume)
        return True

    def is_enabled(self) -> bool:
        """Enabled かどうかを返す。"""
        return self._enabled

    # ----- loading -----

    def auto_load_from_dir(self, directory: str | Path | None = None) -> int:
        """`directory` 内の SE ファイルを走査して名前ベースでロードする。

        BGM 用ファイル（ファイル名が ``bgm_`` で始まるもの）はスキップし、
        ``play_bgm`` 側で個別にパス指定で再生する。

        Returns:
            ロードに成功した SE 数。
        """
        if not self._enabled:
            return 0
        target = Path(directory) if directory is not None else self._asset_dir
        if not target.exists() or not target.is_dir():
            return 0
        loaded = 0
        for path in sorted(target.iterdir()):
            if path.suffix.lower() not in self.SUPPORTED_SE_EXTS:
                continue
            if path.stem.startswith("bgm_"):
                continue
            try:
                sound = pg.mixer.Sound(str(path))
                sound.set_volume(self._se_volume)
            except (pg.error, FileNotFoundError, OSError):
                continue
            self._se_cache[path.stem] = sound
            loaded += 1
        return loaded

    def load_se(self, name: str, path: str | Path) -> bool:
        """個別 SE をロードする。"""
        if not self._enabled:
            return False
        try:
            sound = pg.mixer.Sound(str(path))
            sound.set_volume(self._se_volume)
        except (pg.error, FileNotFoundError, OSError):
            return False
        self._se_cache[name] = sound
        return True

    def has_se(self, name: str) -> bool:
        """Se を持つかどうかを返す。"""
        return name in self._se_cache

    def get_loaded_se_names(self) -> list[str]:
        """Loaded_se_names を返す。"""
        return list(self._se_cache.keys())

    # ----- SoundSink Protocol -----

    def play_se(self, name: str) -> None:
        """Se を再生する。"""
        if not self._enabled:
            return
        sound = self._se_cache.get(name)
        if sound is None:
            return  # 音源未配置 → 静かに無視
        with suppress(pg.error):
            sound.play()

    def play_bgm(self, name: str, loops: int = -1) -> None:
        """BGM を再生する。

        `name` は拡張子なしの名前（例 `bgm_main`）または絶対/相対パス。
        前者の場合は ``assets/sound/<name>.ogg`` 等を自動で探す。
        """
        if not self._enabled:
            return
        path = self._resolve_bgm_path(name)
        if path is None:
            return
        try:
            pg.mixer.music.load(str(path))
            pg.mixer.music.set_volume(self._bgm_volume)
            pg.mixer.music.play(loops=loops)
        except pg.error:
            return
        self._current_bgm = name

    def stop_bgm(self) -> None:
        """Bgm を停止する。"""
        if not self._enabled:
            return
        with suppress(pg.error):
            pg.mixer.music.stop()
        self._current_bgm = None

    # ----- internal -----

    def _resolve_bgm_path(self, name: str) -> Path | None:
        as_path = Path(name)
        if as_path.is_file():
            return as_path
        for ext in self.SUPPORTED_BGM_EXTS:
            candidate = self._asset_dir / f"{name}{ext}"
            if candidate.is_file():
                return candidate
        return None

    # ----- volume -----

    def set_se_volume(self, value: float) -> None:
        """Se_volume を設定する。"""
        self._se_volume = max(0.0, min(1.0, float(value)))
        for sound in self._se_cache.values():
            with suppress(pg.error):
                sound.set_volume(self._se_volume)

    def set_bgm_volume(self, value: float) -> None:
        """Bgm_volume を設定する。"""
        self._bgm_volume = max(0.0, min(1.0, float(value)))
        if self._enabled:
            with suppress(pg.error):
                pg.mixer.music.set_volume(self._bgm_volume)
