---
title: "core/base_player.py：プレイヤー基底クラス"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md"]
---

## 概要

プレイヤーの共通機能（位置、HP、入力受付の枠組み）を `core/base_player.py` に実装する。`Builder`（建築役）と `Fighter`（前線役）が継承する。

## 作業

- `BasePlayer` 基底クラスを定義
- インスタンス変数：
  - `_pos`：座標
  - `_hp`：HP
  - `_player_id`：1 or 2
- メソッド：
  - `update(input_state: dict) -> None`：入力に応じた更新
  - `draw(screen: pg.Surface) -> None`
  - `get_pos() -> tuple[float, float]`
  - `set_pos(x: float, y: float) -> None`
- 入力フォーマットは `network/net_protocol.py` のメッセージと整合性を持たせる（後で調整可）

## 完了条件

- 派生クラス（後続のTaskで実装）を通して画面に表示・移動できる
