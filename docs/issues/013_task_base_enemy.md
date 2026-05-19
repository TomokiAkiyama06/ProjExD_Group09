---
title: "core/base_enemy.py：敵基底クラス（直進移動）"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md", "011_task_fortress.md"]
---

## 概要

敵基底クラスを `core/base_enemy.py` に実装する。NN搭載敵（担当①）、ボス敵・特殊敵（担当④）が継承する。基底クラスでは**拠点に向かって直進する**最小実装にする。

## 作業

- `BaseEnemy` 基底クラスを定義
- インスタンス変数：
  - `_pos`：座標
  - `_hp`：HP
  - `_speed`：移動速度
  - `_damage`：拠点到達時のダメージ
- メソッド：
  - `update(fortress: Fortress) -> None`：拠点方向へ直進移動（派生クラスでオーバーライド可）
  - `draw(screen: pg.Surface) -> None`
  - `take_damage(amount: int) -> None`
  - `is_dead() -> bool`
  - `get_pos() -> tuple[float, float]`
  - `get_hp() -> int`

## 完了条件

- 敵が出現口から拠点へ直進する
- 攻撃を受けるとHPが減り、0で消滅する
