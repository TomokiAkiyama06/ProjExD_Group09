---
title: "combat/special_enemy.py：特殊敵"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["013_task_base_enemy.md"]
---

## 概要

通常敵とは異なる挙動を持つ特殊敵を1〜2種類実装する。

## 作業

- `combat/special_enemy.py` に1〜2種類の特殊敵クラスを実装
- 候補（どれか1〜2種類）：
  - `FastEnemy`：高速・低HP
  - `SplitterEnemy`：撃破時に分裂して小型化
  - `ShieldedEnemy`：盾を持ち、一定ダメージまで無効化
- `BaseEnemy` を継承

## 完了条件

- 通常敵とは明らかに異なる挙動の特殊敵が出現する
- ゲームに変化が生まれる
