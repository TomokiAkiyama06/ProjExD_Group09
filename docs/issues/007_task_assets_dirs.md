---
title: "assets/ ディレクトリ構造を作成"
labels: ["task", "infra"]
assignees: []
milestone: null
parent: "002_epic_setup.md"
depends_on: []
---

## 概要

素材（画像・音声・フォント）を格納するディレクトリ構造を作成する。

## 作業

以下のディレクトリを作成し、各々に `.gitkeep` を置く（Gitは空ディレクトリを管理しないため）：

- `assets/fig/.gitkeep`
- `assets/sound/.gitkeep`
- `assets/font/.gitkeep`

## 完了条件

- `git clone` 後にディレクトリ構造が再現される
- 後続のTaskで `assets/fig/enemy.png` のようにファイルを置けば、コードから相対パスで参照できる
