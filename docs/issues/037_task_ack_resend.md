---
title: "重要イベントの ACK・再送機構"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["033_task_net_server_recv.md", "036_task_net_client.md"]
---

## 概要

UDPはパケットロスが起きるので、タワー設置などの重要イベントは「ACKが返るまで再送」する機構で確実に届ける。

## 作業

- `NetServer` / `NetClient` 双方に以下の機能を追加：
  - `send_event(event: dict, ack_required: bool = True) -> None`：イベント送信
  - `_pending_events`：ACK待ちイベントのキャッシュ（seq番号でキー管理）
  - 一定時間（例：500ms）ACKが返らなければ再送
  - 最大再送回数（例：5回）に達したらログを出す
  - ACK受信時に該当イベントを `_pending_events` から削除

## 完了条件

- パケットを意図的に落とすシミュレーション（10%ドロップなど）でも、最終的にイベントが届く
- ACKを受信したイベントは再送されない
