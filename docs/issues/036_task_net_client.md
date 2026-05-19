---
title: "network/net_client.py：接続要求と操作送信"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["031_task_net_protocol_serde.md", "034_task_handshake.md"]
---

## 概要

クライアント側のUDP通信機能を実装。ホストへの接続要求と、30Hzでの操作送信を担う。

## 作業

- `network/net_client.py` に `NetClient` クラスを実装
- 主な機能：
  - `connect(host: str, port: int) -> bool`：`connect`メッセージを送信、`connect_ok`を待つ
  - `send_input(input_dict: dict) -> None`：操作メッセージを送信（30Hz）
  - 受信スレッドで state を受信し、内部バッファに格納
  - メインスレッド側から `poll_state() -> dict | None` で最新stateを取り出す

## 完了条件

- ホストに接続して player_id を取得できる
- 接続後、毎フレーム操作を送信できる
- ホストからの state を受信できる
