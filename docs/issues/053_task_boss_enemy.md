---
title: "combat/boss_enemy.py：ボス敵"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["013_task_base_enemy.md"]
---

## 概要

ウェーブの節目（例：5の倍数）に出現する高HP・特殊行動パターンのボス敵を実装する。

## 作業

- `combat/boss_enemy.py` に `BossEnemy` クラスを実装
- `BaseEnemy` を継承
- 特徴：
  - HP：通常敵の10〜20倍
  - サイズ：大きめ
  - 特殊行動：定期的に範囲攻撃、または周囲の通常敵にバフを与える
  - 撃破時の演出（爆発・大きなエフェクト）

## 完了条件

- ウェーブの節目（5の倍数など）にボスが出現する
- 通常敵よりタフ・特殊な動きをする
- 撃破時に派手な演出が出る
