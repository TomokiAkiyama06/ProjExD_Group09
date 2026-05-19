---
title: "combat/weapons.py：武器バリエーション3種類"
labels: ["task", "combat"]
assignees: []
milestone: null
parent: "047_epic_combat.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

前線役プレイヤーが使用する武器を3種類実装する。

## 作業

- `combat/weapons.py` に `BaseWeapon` 基底クラス
- 3種類の派生クラス：
  - `MeleeWeapon`：近接武器（射程短い、ダメージ高、連射速度普通）
  - `RangedWeapon`：遠距離武器（射程長い、ダメージ普通、連射速度速い）
  - `AreaWeapon`：範囲武器（範囲攻撃、ダメージ普通、連射速度遅い）

## 完了条件

- 3種類の武器がそれぞれ異なる挙動で攻撃できる
