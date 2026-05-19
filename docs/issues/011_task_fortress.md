---
title: "core/fortress.py：拠点クラスの実装"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md"]
---

## 概要

HPを持つ拠点（コア）クラスを `core/fortress.py` に実装する。敵が触れるとHPが減り、HP0で敗北判定となる。

## 作業

- `Fortress` クラスを定義
- インスタンス変数（`_変数名` 形式）：
  - `_hp`：現在HP
  - `_max_hp`：最大HP
  - `_pos`：座標
- メソッド：
  - `get_hp() -> int`
  - `set_hp(value: int) -> None`
  - `take_damage(amount: int) -> None`
  - `is_destroyed() -> bool`
  - `draw(screen: pg.Surface) -> None`

## 完了条件

- 敵が拠点に接触するとHPが減る
- HPが0になると `is_destroyed()` が True を返す
- HPバーが画面に描画される
