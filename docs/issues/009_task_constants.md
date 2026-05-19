---
title: "core/constants.py の基本定数を定義"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

全プロジェクトで共有する定数を `core/constants.py` に定義する。マジックナンバーをコード中に直接書かないため、ここに集約する。

## 作業

- 画面サイズ、FPS、色定義
- ゲームバランス基本値（初期リソース、拠点HP）
- セクションコメントで担当ごとのエリアを分けておく（進化AI、ネットワーク等の空セクションを用意しておく）

### 記述例

```python
"""全プロジェクトで共有する定数。"""

# ===== 画面・描画（ベース） =====
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60

# ===== 色 =====
COLOR_BG: tuple[int, int, int] = (20, 20, 30)
COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)

# ===== ゲームバランス（ベース） =====
INITIAL_GOLD: int = 100
FORTRESS_MAX_HP: int = 1000

# ===== 進化AI（担当①） =====
# 担当①が記述

# ===== ネットワーク（担当②） =====
# 担当②が記述
```

## 完了条件

- 他のモジュールから `from core.constants import SCREEN_WIDTH` が成功する
- セクションが分かれていて、他の担当者が自分のセクションに追記できる
