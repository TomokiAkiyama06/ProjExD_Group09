---
title: ".gitignore を作成"
labels: ["task", "infra"]
assignees: []
milestone: null
parent: "002_epic_setup.md"
depends_on: []
---

## 概要

不要なファイルが Git 管理されないよう `.gitignore` をリポジトリのルートに作成する。

## 作業

- `.gitignore` をルートに作成
- 以下の内容を記述：

```
__pycache__/
*.pyc
*.pyo
.vscode/
.DS_Store
*.log
.pytest_cache/
```

## 完了条件

- `git status` でPythonのキャッシュやIDEの設定ファイルが表示されない
