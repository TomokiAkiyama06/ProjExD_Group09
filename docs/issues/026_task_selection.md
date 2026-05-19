---
title: "選択処理（エリート + トーナメント）"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["025_task_fitness.md"]
---

## 概要

次世代の親個体を選ぶ処理を実装する。エリート選択（上位個体をそのまま残す）とトーナメント選択（複数体から最良を選ぶ）の併用。

## 作業

`EvolutionManager` に以下のメソッドを追加：

- `select_elites(population: list, fitness_list: list[float], n_elite: int) -> list`
  - 上位 `n_elite` 個体（デフォルトは全体の20%）を返す
- `tournament_select(population: list, fitness_list: list[float], k: int = 3) -> object`
  - ランダムに k 体抽出し、その中で最も適応度の高い個体を返す

## 完了条件

- 個体群リストと適応度リストを入力として、次世代の親リストが得られる
- エリート率・トーナメントサイズは `constants.py` から変更できる
