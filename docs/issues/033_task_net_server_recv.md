---
title: "network/net_server.py：ソケット初期化と受信スレッド"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["031_task_net_protocol_serde.md"]
---

## 概要

UDPサーバのソケットをバインドし、受信スレッドを起動する。受信メッセージはキューに格納してメインスレッドが取り出せるようにする。

## 作業

- `network/net_server.py` に `NetServer` クラスを実装
- ソケット初期化：
  ```python
  import socket
  self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  self._sock.bind(("0.0.0.0", NET_PORT))
  ```
- 受信スレッド：
  - `threading.Thread` で起動
  - 受信ループで `recvfrom()`
  - デシリアライズして `queue.Queue` に格納
- メインスレッド側から `poll_messages() -> list[tuple[addr, dict]]` でキューを取り出す

## 完了条件

- ローカルで送られたパケットを受信して queue に積める
- 受信スレッドが正常に起動・停止できる
- 例外処理が入っている
