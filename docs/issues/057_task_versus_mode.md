---
title: "presentation/versus_mode.py：対戦モードのゲームロジック"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["030_epic_network.md"]
---

## 概要

2人がそれぞれの砦を持ち、互いに敵を送り合う対戦モードのゲームロジックを実装する。協力モードのネット基盤を流用。

## 作業

- `presentation/versus_mode.py` に `VersusGame` クラスを実装
- `HostGame` から派生または並列の構造で実装
- 主な変更点：
  - 各プレイヤーが自分の砦を持つ
  - 敵スポーン先がプレイヤーごとに分離
  - リソースは個別管理（次のTask #58）
  - ネット同期は協力モードのプロトコルを拡張

## 完了条件

- 2人が別々の砦を持ってゲームが進行する
- ネット越しに状態同期できる
