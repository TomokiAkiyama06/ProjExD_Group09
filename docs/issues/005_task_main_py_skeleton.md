---
title: "main.py の雛形を作成（引数分岐つき）"
labels: ["task", "infra", "core"]
assignees: []
milestone: null
parent: "002_epic_setup.md"
depends_on: []
---

## 概要

エントリーポイント `main.py` の雛形を作成する。授業の必須要件である `os.chdir` を冒頭に記述し、起動モード（host / client / solo）の引数分岐を実装する。

## 作業

- `main.py` をルートに作成
- 冒頭に以下のコードを記述（**授業の必須要件**）：

```python
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
```

- `argparse` で以下の引数分岐を実装：
  - `--host`：ホストモード（プレイヤー1、権威サーバ）
  - `--client --ip=<IP>`：クライアントモード（プレイヤー2）
  - `--solo`：1台2プレイヤーモード（フォールバック）

- 各モードの実装は仮で `print("not implemented")` または `pass` でOK（後続のTaskで埋める）

## 完了条件

- `python main.py --solo` でエラーが出ない
- `python main.py --host` でエラーが出ない
- `python main.py --client --ip=127.0.0.1` でエラーが出ない
