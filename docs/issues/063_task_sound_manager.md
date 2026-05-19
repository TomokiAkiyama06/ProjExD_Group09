---
title: "presentation/sound_manager.py：BGM・SE管理の骨格"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

BGM・効果音を統一的に管理するクラスを実装する。

## 作業

- `presentation/sound_manager.py` に `SoundManager` クラス
- 初期化：
  ```python
  import pygame as pg
  pg.mixer.init()
  ```
- 機能：
  - `play_bgm(path: str, loops: int = -1) -> None`：BGM再生
  - `stop_bgm() -> None`：BGM停止
  - `play_se(name: str) -> None`：効果音再生（名前から事前ロード済みSoundを引く）
  - `_se_cache`：効果音ファイルのキャッシュ（クラス変数）
- 効果音ファイルは `assets/sound/` から読む

## 完了条件

- BGMが再生でき、停止できる
- 効果音を複数同時に鳴らせる
