---
title: "担当③：タワー属性とアップグレード"
labels: ["epic", "towers", "priority:mid"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["014_task_base_tower_bullet.md"]
---

## 概要

炎・氷・雷・物理の4属性タワーを実装する。各属性ごとに敵への効果が異なり、戦略性を生む。

## 担当

担当③

## Task 一覧

- [ ] `towers/fire_tower.py`：火炎タワー（範囲ダメージ）（`041_task_fire_tower.md`）
- [ ] `towers/ice_tower.py`：氷タワー（速度低下）（`042_task_ice_tower.md`）
- [ ] `towers/lightning_tower.py`：雷タワー（チェイン攻撃）（`043_task_lightning_tower.md`）
- [ ] `towers/physical_tower.py`：物理タワー（高単発火力）（`044_task_physical_tower.md`）
- [ ] `towers/tower_upgrade.py`：レベルアップシステム（`045_task_tower_upgrade.md`）
- [ ] タワー選択UI（`046_task_tower_selector_ui.md`）

## 完了条件

- 4属性のタワーがすべて設置・攻撃できる
- アップグレードでステータスが上昇する
