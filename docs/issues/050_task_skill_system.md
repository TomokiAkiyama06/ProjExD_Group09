---
title: "combat/fighter_skills.py：スキルシステムの骨格"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["020_task_player2_input.md"]
---

## 概要

スキルの共通仕組み（クールタイム管理、発動判定）を実装する。個別スキルは後続Task。

## 作業

- `combat/fighter_skills.py` に `BaseSkill` 基底クラス
- 共通機能：
  - `cooldown`：クールタイム秒数
  - `last_used_tick`：最後に使用した時刻
  - `can_use(now) -> bool`：使用可能か判定
  - `activate(player, world) -> None`：発動処理（派生クラスでオーバーライド）
- Kキー押下で現在のスキルを発動する仕組み
- HUDにクールタイム表示用のフックを用意（担当⑤と連携）

## 完了条件

- スキル基底クラスがあり、派生クラスで具体的なスキルを実装できる構造になっている
- クールタイム待機の仕組みが動く
