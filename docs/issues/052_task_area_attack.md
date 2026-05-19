---
title: "スキル：範囲攻撃"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["050_task_skill_system.md"]
---

## 概要

プレイヤー周囲一定範囲の敵にダメージを与える範囲攻撃スキルを実装する。

## 作業

- `combat/fighter_skills.py` に `AreaAttackSkill` クラス
- 発動時：
  - プレイヤーを中心に半径 `_radius` の範囲内の敵にダメージ
  - 視覚エフェクト（円形の波紋など、`effects.py` と連携）
- クールタイム：例 12秒

## 完了条件

- 範囲スキルが発動し、複数の敵に同時ヒットする
- エフェクトで範囲が視覚的にわかる
