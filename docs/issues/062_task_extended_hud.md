---
title: "presentation/extended_hud.py：詳細HUD"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["016_task_base_hud.md"]
---

## 概要

`BaseHUD` を拡張して、詳細情報を表示するリッチなHUDを実装する。

## 作業

- `presentation/extended_hud.py` に `ExtendedHUD` クラス
- `BaseHUD` を継承
- 追加表示項目：
  - タワー選択時のステータス（ダメージ・射程・連射速度・コスト）
  - スキルアイコンとクールタイム
  - 世代番号・現世代の最強個体の適応度
  - 対戦モード時：相手の拠点HP

## 完了条件

- 視認性の高いHUDが表示される
- ゲームに必要な情報がほとんど画面で確認できる
