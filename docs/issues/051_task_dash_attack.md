---
title: "スキル：ダッシュ攻撃"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["050_task_skill_system.md"]
---

## 概要

短時間で前方に高速移動し、通過した敵にダメージを与えるダッシュ攻撃スキルを実装する。

## 作業

- `combat/fighter_skills.py` に `DashAttackSkill` クラス
- 発動時：
  - プレイヤーが向いている方向に短時間で高速移動
  - 移動中に接触した敵にダメージ
  - 移動中は無敵 or 軽減
- クールタイム：例 8秒

## 完了条件

- ダッシュスキルが発動し、移動中に敵にヒットする
- クールタイム中は再発動できない
