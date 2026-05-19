---
title: "towers/ice_tower.py：氷タワー（速度低下）"
labels: ["task", "towers"]
assignees: []
milestone: null
parent: "040_epic_towers.md"
depends_on: ["014_task_base_tower_bullet.md"]
---

## 概要

敵の速度を一定時間下げる氷タワーを実装する。

## 作業

- `towers/ice_tower.py` に `IceTower` クラスを実装
- `BaseTower` を継承
- 敵に当たった弾は：
  - ダメージを与える
  - 敵の `_speed_factor` を一定時間（例：3秒）下げる
- `BaseEnemy` に「速度低下バフ」を受け取るインターフェース（`apply_slow(factor, duration)` など）が必要なら、担当①と相談のうえ `core/base_enemy.py` に追加

## 完了条件

- 氷タワーに撃たれた敵が遅くなる
- 効果時間が経つと元の速度に戻る
