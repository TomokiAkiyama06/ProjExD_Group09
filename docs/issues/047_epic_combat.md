---
title: "担当④：前線戦闘と演出"
labels: ["epic", "combat", "priority:mid"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["012_task_base_player.md", "013_task_base_enemy.md"]
---

## 概要

前線役プレイヤーの武器・スキル、ボス敵・特殊敵、視覚演出（パーティクル）を実装する。発表で映える派手な要素。

## 担当

担当④

## Task 一覧

- [ ] `combat/weapons.py`：武器バリエーション3種類（`048_task_weapons.md`）
- [ ] 武器切替UI（`049_task_weapon_switch_ui.md`）
- [ ] `combat/fighter_skills.py`：スキルシステムの骨格（`050_task_skill_system.md`）
- [ ] スキル：ダッシュ攻撃（`051_task_dash_attack.md`）
- [ ] スキル：範囲攻撃（`052_task_area_attack.md`）
- [ ] `combat/boss_enemy.py`：ボス敵（`053_task_boss_enemy.md`）
- [ ] `combat/special_enemy.py`：特殊敵（`054_task_special_enemy.md`）
- [ ] `combat/effects.py`：パーティクルエフェクト（`055_task_effects.md`）

## 完了条件

- 前線役プレイヤーが武器切替・スキル発動できる
- ボスがウェーブの節目に出現する
- 視覚的に「攻撃した」「倒した」感がはっきり出る
