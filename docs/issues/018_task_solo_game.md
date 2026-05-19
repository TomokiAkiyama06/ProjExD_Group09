---
title: "core/solo_game.py：SoloGameクラス"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "017_epic_solo_mode.md"
depends_on: ["010_task_game_base.md", "012_task_base_player.md"]
---

## 概要

`Game` を継承して、1台のPCで両プレイヤーを操作できる `SoloGame` クラスを実装する。

## 作業

- `core/solo_game.py` に `SoloGame` クラスを実装
- `Game` を継承
- `Builder`（プレイヤー1）と `Fighter`（プレイヤー2）を両方ローカルでインスタンス化
- `update()` 内で両プレイヤーの入力を処理
- `main.py --solo` から呼び出される

## 完了条件

- `python main.py --solo` でゲーム画面が立ち上がる
- 何もしなくてもクラッシュしない（敵が直進してくる程度の動きはあるとよい）
