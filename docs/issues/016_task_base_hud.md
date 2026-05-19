---
title: "core/base_hud.py：HUD基底"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md"]
---

## 概要

ゲーム中に表示する情報（拠点HP、リソース、ウェーブ番号、世代番号）を表示する HUD 基底クラスを実装する。担当⑤の `ExtendedHUD` が継承する。

## 作業

- `BaseHUD` クラスを `core/base_hud.py` に実装
- 表示項目：
  - 拠点HP（バー表示）
  - 現在のリソース
  - 現在のウェーブ番号
  - 現在の世代番号（進化AIが進めば更新される）
- メソッド：
  - `draw(screen: pg.Surface, game_state: dict) -> None`
- `game_state` には `core_hp`, `resource`, `wave`, `generation` 等が入る

## 完了条件

- ゲーム中に画面上部または下部に各種情報が表示される
- 値はゲーム状態の変化に応じてリアルタイムで更新される
