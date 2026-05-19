---
title: "共通基本機能：core パッケージ"
labels: ["epic", "core", "priority:high"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["002_epic_setup.md"]
---

## 概要

全員が依存するベース部分を実装する。他のメンバーはこのパッケージを継承・利用するため、**最優先で完成させる**。

## 担当

基本機能担当（代表者含む2人）

## Task 一覧

- [ ] `core/constants.py` の基本定数を定義（`009_task_constants.md`）
- [ ] `core/game.py`：Game基底クラス（`010_task_game_base.md`）
- [ ] `core/fortress.py`：拠点クラス（`011_task_fortress.md`）
- [ ] `core/base_player.py`：プレイヤー基底（`012_task_base_player.md`）
- [ ] `core/base_enemy.py`：敵基底（直進移動）（`013_task_base_enemy.md`）
- [ ] `core/base_tower.py` + `core/bullet.py`：タワー＆弾の基底（`014_task_base_tower_bullet.md`）
- [ ] `core/world.py` + `core/wave_manager.py`：マップとウェーブ管理（`015_task_world_wave.md`）
- [ ] `core/base_hud.py`：HUD基底（`016_task_base_hud.md`）

## 完了条件

- 1種類のタワーで1種類の敵を撃てる
- 拠点に敵が到達するとHPが減る
- ウェーブが進む
