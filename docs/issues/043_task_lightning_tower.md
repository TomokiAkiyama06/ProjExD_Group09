---
title: "towers/lightning_tower.py：雷タワー（チェイン攻撃）"
labels: ["task", "towers"]
assignees: []
milestone: null
parent: "040_epic_towers.md"
depends_on: ["014_task_base_tower_bullet.md"]
---

## 概要

最初の敵から近隣の敵へ連鎖（チェイン）してダメージを与える雷タワーを実装する。

## 作業

- `towers/lightning_tower.py` に `LightningTower` クラスを実装
- 攻撃時：
  1. 射程内の最も近い敵にダメージ
  2. その敵から半径 `_chain_radius` 内の別の敵を探す
  3. 見つかればダメージ（ただし減衰、例：80%）
  4. 最大 `_chain_count` 回まで繰り返す
- 視覚的にチェインのライン描画（簡易でOK）

## 完了条件

- 雷タワーが複数の敵に連鎖ダメージを与えられる
- チェインの様子が画面で確認できる
