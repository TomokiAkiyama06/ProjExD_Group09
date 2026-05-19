---
title: "requirements.txt を作成"
labels: ["task", "infra"]
assignees: []
milestone: null
parent: "002_epic_setup.md"
depends_on: []
---

## 概要

プロジェクトに必要な Python パッケージを記述した `requirements.txt` をリポジトリのルートに作成する。

## 作業

- `requirements.txt` をルートに作成
- 以下の内容を記述：

```
pygame>=2.1
numpy>=1.24
```

## 完了条件

- `pip install -r requirements.txt` がエラーなく実行できる
- メンバー全員が同じ環境を構築できる
