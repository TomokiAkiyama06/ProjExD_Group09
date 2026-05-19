---
title: "対戦モード：敵送信コマンドのUI"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["057_task_versus_mode.md"]
---

## 概要

自分が育てたNNプールから敵を選んで相手の砦に送る機能を実装する。

## 作業

- 敵送信ボタン or キー入力（例：B キーで送信メニューを開く）
- 送れる敵の種類を選ぶUI（自分のNNプールから1体選択）
- リソース消費（敵の強さに応じてコスト）
- ネット越しに「敵を送る」イベントを相手側へ送信し、相手の砦に出現させる

## 完了条件

- 敵を相手の砦に送れる
- 送った敵が相手側の画面に出現する
- リソースが消費される
