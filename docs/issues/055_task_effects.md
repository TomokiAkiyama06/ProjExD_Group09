---
title: "combat/effects.py：パーティクルエフェクト"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

ゲーム中の各種イベントに視覚的演出を加えるエフェクトシステムを実装する。

## 作業

- `combat/effects.py` に `EffectManager` クラスを実装
- 機能：
  - パーティクル個別オブジェクト（座標・速度・寿命・色を持つ）
  - スポーン関数：`spawn_explosion(pos)`, `spawn_hit(pos)`, `spawn_muzzle_flash(pos, dir)` 等
  - 毎フレーム `update()` で全パーティクルを更新、寿命切れを削除
  - `draw(screen)` で全パーティクルを描画
- 主なエフェクト：
  - 敵撃破時の爆発
  - タワー攻撃時のマズルフラッシュ
  - ヒット時のフラッシュ・火花

## 完了条件

- 敵を撃破すると爆発エフェクトが出る
- タワーが撃つと発射エフェクトが出る
- 視覚的に「攻撃した」「倒した」感がはっきりする
