---
title: "towers/tower_upgrade.py：レベルアップシステム"
labels: ["task", "towers"]
assignees: []
milestone: null
parent: "040_epic_towers.md"
depends_on: ["041_task_fire_tower.md", "042_task_ice_tower.md", "043_task_lightning_tower.md", "044_task_physical_tower.md"]
---

## 概要

各タワーをLv1〜Lv3にアップグレードできるシステムを実装する。

## 作業

- `towers/tower_upgrade.py` に `TowerUpgrade` クラス（またはユーティリティ関数群）
- 各タワーをアップグレード可能：Lv1 → Lv2 → Lv3
- アップグレードでステータス上昇：
  - ダメージ
  - 射程
  - 連射速度
- アップグレードコストを `constants.py` に定義
- 売却機能（コストの50%が戻る）

## 完了条件

- リソース消費でタワーがアップグレードできる
- ステータスが上昇する（数値が画面で確認できる）
- 売却でリソースが返ってくる
