---
title: "対戦モード：個別リソース管理"
labels: ["task", "presentation"]
assignees: []
milestone: null
parent: "056_epic_presentation.md"
depends_on: ["057_task_versus_mode.md"]
---

## 概要

対戦モードでは共有リソースを個別リソースに切り替える。各プレイヤーが自分の砦のためにリソースを使う。

## 作業

- `VersusGame` 内で各プレイヤーごとにリソース変数を分離
- リソース獲得：自分の砦に来た敵を撃破した分だけ自分のリソースに加算
- リソース消費：自分のタワー設置・アップグレード・敵送信に使う

## 完了条件

- リソースが2人分独立して管理される
- HUDで自分のリソース・相手のリソースが見える
