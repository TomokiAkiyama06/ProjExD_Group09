---
title: "パッケージ用 __init__.py を配置"
labels: ["task", "infra"]
assignees: []
milestone: null
parent: "002_epic_setup.md"
depends_on: []
---

## 概要

全サブパッケージを Python パッケージとして認識させるため、空の `__init__.py` を配置する。

## 作業

以下のディレクトリに空の `__init__.py` を作成：

- `core/__init__.py`
- `evolution/__init__.py`
- `network/__init__.py`
- `towers/__init__.py`
- `combat/__init__.py`
- `presentation/__init__.py`

## 完了条件

- 各パッケージから絶対インポートできる（例：`from core.constants import X` が成功する）
