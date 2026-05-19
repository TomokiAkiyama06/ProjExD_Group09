---
title: "network/net_protocol.py：JSON↔bytes 変換関数"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

UDP送受信で使うシリアライズ・デシリアライズ関数を実装する。Python標準の `json` モジュールを使用。

## 作業

- `network/net_protocol.py` に以下の関数を実装：
  - `serialize(msg: dict) -> bytes`
  - `deserialize(data: bytes) -> dict`
- 例外処理を入れる（不正データ受信時に落ちないように）

### 例

```python
import json

def serialize(msg: dict) -> bytes:
    """dictをbytesに変換する。"""
    return json.dumps(msg, ensure_ascii=False).encode("utf-8")

def deserialize(data: bytes) -> dict:
    """bytesをdictに変換する。失敗時は空dictを返す。"""
    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
```

## 完了条件

- 任意の dict を bytes 化して戻せる
- 不正な bytes を渡しても例外で落ちない
