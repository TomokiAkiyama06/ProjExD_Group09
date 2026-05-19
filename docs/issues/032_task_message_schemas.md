---
title: "メッセージ型定義（input/state/event/connect/ping）"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["031_task_net_protocol_serde.md"]
---

## 概要

ホスト・クライアント間でやり取りするメッセージの種類とフォーマットを定義する。

## 作業

`network/net_protocol.py` に以下のメッセージ型を定数または `TypedDict` / `dataclass` で定義：

### メッセージ種別

1. **input**（クライアント→ホスト）：プレイヤー操作
2. **state**（ホスト→クライアント）：ゲーム状態
3. **event**（双方向）：重要イベント（タワー設置など）
4. **connect** / **connect_ok**：ハンドシェイク
5. **ping** / **pong**：ハートビート
6. **ack**：イベント受信確認

### スキーマ例（DESIGN.md 2.3節参照）

```json
// input
{"type": "input", "seq": 142, "player_id": 2, "input": {"move": [0.5, -1.0], ...}}

// state
{"type": "state", "seq": 1024, "enemies": [...], "towers": [...], ...}

// event
{"type": "event", "seq": 305, "event": "tower_placed", "data": {...}, "ack_required": true}
```

## 完了条件

- 全メッセージ型のサンプルを生成・パースできる
- `network/test_network.py` にサンプル生成のテストを追加
