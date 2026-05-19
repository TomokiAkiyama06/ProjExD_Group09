---
title: "担当①：進化AI（ニューラルネット + GA）"
labels: ["epic", "evolution", "priority:high"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["002_epic_setup.md"]
---

## 概要

敵が遺伝的アルゴリズムで世代ごとに進化する仕組みを実装する。**本プロジェクトの最大の差別化要素**。基本機能の完成を待たずに、`evolution/test_evolution.py` で単独テストしながら開発できる。

## 担当

担当①（エース1）

## Task 一覧

- [ ] `evolution/neural_net.py`：NNクラスの骨格と forward 実装（`022_task_nn_forward.md`）
- [ ] NNの重み取得・設定メソッド（交叉用）（`023_task_nn_weights.md`）
- [ ] NNの単体テスト作成（`024_task_nn_unittest.md`）
- [ ] `evolution/evolution_manager.py`：適応度計算（`025_task_fitness.md`）
- [ ] 選択処理（エリート + トーナメント）（`026_task_selection.md`）
- [ ] 交叉処理（一様交叉）（`027_task_crossover.md`）
- [ ] 突然変異処理（`028_task_mutation.md`）
- [ ] `evolution/evolved_enemy.py`：NN搭載敵クラス（`029_task_evolved_enemy.md`）

## 完了条件

- `python -m evolution.test_evolution` で全テストが通る
- ゲーム本体に組み込んだ際、世代を経るごとに敵の動きが変化していくことが観察できる

## 注意

- NN自体はネットワーク通信に乗せない（位置情報のみ送る）→ 担当②と疎結合
- PyTorch / TensorFlow を導入しない（NumPyのみで実装）
