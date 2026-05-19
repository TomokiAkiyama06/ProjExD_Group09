---
title: "presentation/evolution_graph.py：適応度グラフ表示"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["021_epic_evolution_ai.md"]
---

## 概要

世代ごとの最高適応度・平均適応度をリアルタイムでグラフ表示する。発表で「敵が進化している」ことを視覚的に示す重要要素。

## 作業

- `presentation/evolution_graph.py` に `EvolutionGraph` クラスを実装
- pygame の描画で実装（matplotlib は重いので避ける）
- 表示内容：
  - 横軸：世代番号
  - 縦軸：適応度
  - 各世代の最高値と平均値を線グラフで描画
- 担当①と連携してデータフォーマットを決める（CSV or list[dict]）

## 完了条件

- ゲーム画面の一角にグラフが常時表示される
- 世代を経るごとに線が伸びていく様子が見える
