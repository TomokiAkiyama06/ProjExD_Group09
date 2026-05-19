---
title: "towers/physical_tower.py：物理タワー（高単発火力）"
labels: ["task", "towers"]
assignees: []
milestone: null
parent: "040_epic_towers.md"
depends_on: ["014_task_base_tower_bullet.md"]
---

## 概要

連射速度は遅いが単発で高火力の物理タワーを実装する。

## 作業

- `towers/physical_tower.py` に `PhysicalTower` クラスを実装
- 特徴：
  - 連射間隔：長め
  - ダメージ：他タワーの2〜3倍
  - 射程：長め
  - 装甲貫通効果（任意：敵のHP割合に応じた追加ダメージなど）

## 完了条件

- 物理タワーが高ダメージを単体に与えられる
- ボス級の高HP敵にも有効である
