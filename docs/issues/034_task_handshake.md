---
title: "クライアント接続管理（ハンドシェイク）"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["033_task_net_server_recv.md"]
---

## 概要

クライアントからの `connect` メッセージを受け取り、`player_id` を割り当てて `connect_ok` を返信する。接続中クライアントの情報を保持する。

## 作業

- `NetServer` に以下を追加：
  - `_clients`: dict[addr, PlayerInfo] - 接続中クライアント
  - `handle_connect(addr, msg) -> None`：接続要求を処理し、player_idを割り当てて connect_ok を返信
- `PlayerInfo` クラス（dataclassでOK）：
  - `player_id`, `name`, `last_seen_tick`, `last_seq`

## 完了条件

- クライアント側で `connect` を送ると、`connect_ok` が返ってくる
- 複数のクライアントが接続できる（player_id 1, 2, ...）
