---
title: "担当②：UDPネットワーク"
labels: ["epic", "network", "priority:high"]
assignees: []
milestone: null
parent: "001_epic_meta.md"
depends_on: ["002_epic_setup.md"]
---

## 概要

LAN内2台のPC間でUDP通信を行う基盤を実装。権威サーバ型（authoritative server）：ホスト側が全ゲームロジックを保持し、クライアントは描画のみ。

## 担当

担当②（エース2）

## Task 一覧

- [ ] `network/net_protocol.py`：JSON↔bytes 変換関数（`031_task_net_protocol_serde.md`）
- [ ] メッセージ型定義（input/state/event/connect/ping）（`032_task_message_schemas.md`）
- [ ] `network/net_server.py`：ソケット初期化と受信スレッド（`033_task_net_server_recv.md`）
- [ ] クライアント接続管理（ハンドシェイク）（`034_task_handshake.md`）
- [ ] 状態ブロードキャスト（20Hz）（`035_task_state_broadcast.md`）
- [ ] `network/net_client.py`：接続要求と操作送信（`036_task_net_client.md`）
- [ ] 重要イベントの ACK・再送機構（`037_task_ack_resend.md`）
- [ ] ハートビート・タイムアウト検知（`038_task_heartbeat.md`）
- [ ] `network/state_buffer.py`：補間処理（`039_task_state_buffer.md`）

## 完了条件

- 同一PC内で2プロセス起動して、ゲーム状態と操作のやり取りが成功する
- LAN で別PC同士の接続が確認できる

## 注意

- スレッド間のデータ受け渡しは `queue.Queue` を使う
- 例外処理を必ず入れる（接続断対応）
- 進化AIとは疎結合：NN自体は通信に乗せず、計算結果（位置）のみ送る
