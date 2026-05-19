---
title: "初期セットアップ"
labels: ["epic", "infra", "priority:high"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: []
---

## 概要

リポジトリの初期構造を整える。各メンバーが作業を開始できる状態にする。

## 担当

代表者

## Task 一覧

- [ ] `requirements.txt` を作成（`003_task_requirements_txt.md`）
- [ ] `.gitignore` を作成（`004_task_gitignore.md`）
- [ ] `main.py` の雛形を作成（`005_task_main_py_skeleton.md`）
- [ ] パッケージ用 `__init__.py` を配置（`006_task_init_files.md`）
- [ ] `assets/` ディレクトリ構造を作成（`007_task_assets_dirs.md`）

## 完了条件

メンバーが `git clone` した直後に `python main.py --solo` でエラーが出ない（ゲームは動かなくてもimportエラーがないこと）。
