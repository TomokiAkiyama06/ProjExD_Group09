---
title: "共通基本機能：soloモード"
labels: ["epic", "core", "priority:high"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["008_epic_core_package.md"]
---

## 概要

ネットワークなしで1台のPCで両プレイヤーを操作できるモード。デバッグ環境＆発表時のフォールバック。

## 担当

基本機能担当

## Task 一覧

- [ ] `core/solo_game.py`：SoloGameクラス（`018_task_solo_game.md`）
- [ ] プレイヤー1の操作（マウス＋数字キー）実装（`019_task_player1_input.md`）
- [ ] プレイヤー2の操作（WASD＋JKL）実装（`020_task_player2_input.md`）

## 完了条件

- `python main.py --solo` でゲームが起動する
- 1台のPCで建築役と前線役を同時に操作できる
