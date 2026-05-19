---
title: "towers/fire_tower.py：火炎タワー（範囲ダメージ）"
labels: ["task", "towers"]
assignees: []
milestone: null
parent: "040_epic_towers.md"
depends_on: ["014_task_base_tower_bullet.md"]
---

## 概要

範囲ダメージを与える火炎タワーを実装する。着弾点周囲の敵すべてにダメージを与える。

## 作業

- `towers/fire_tower.py` に `FireTower` クラスを実装
- `BaseTower` を継承
- 専用の弾クラス `FireBullet`（または `Bullet` 派生）：
  - 着弾時に半径 `_explosion_radius` 内の敵すべてにダメージ
- パラメータは `constants.py` の `FIRE_*` セクションに集約

## 完了条件

- 火炎タワーが設置・発射できる
- 範囲内の複数の敵に同時ダメージを与えられる
