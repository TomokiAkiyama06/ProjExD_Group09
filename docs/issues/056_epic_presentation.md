---
title: "担当⑤：対戦・可視化・サウンド"
labels: ["epic", "presentation", "priority:mid"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["030_epic_network.md"]
---

## 概要

対戦モード、進化グラフ、HUD拡張、BGM・SEを実装。発表で映える要素を担当。対戦モードはネットワーク基盤に依存するため、それまでは進化グラフ・HUD・サウンドから着手する。

## 担当

担当⑤

## Task 一覧

- [ ] `presentation/versus_mode.py`：対戦モードのゲームロジック（`057_task_versus_mode.md`）
- [ ] 対戦モード：個別リソース管理（`058_task_versus_resource.md`）
- [ ] 対戦モード：敵送信コマンドのUI（`059_task_versus_send_enemy.md`）
- [ ] 対戦モード：勝敗判定（`060_task_versus_winlose.md`）
- [ ] `presentation/evolution_graph.py`：適応度グラフ表示（`061_task_evolution_graph.md`）
- [ ] `presentation/extended_hud.py`：詳細HUD（`062_task_extended_hud.md`）
- [ ] `presentation/sound_manager.py`：BGM・SE管理の骨格（`063_task_sound_manager.md`）
- [ ] 各シーンへのサウンド組み込み（`064_task_sound_integration.md`）

## 完了条件

- 対戦モードで勝敗が決まるまでプレイできる
- 進化の様子がグラフで見える
- BGMと効果音でゲームに没入感がある
