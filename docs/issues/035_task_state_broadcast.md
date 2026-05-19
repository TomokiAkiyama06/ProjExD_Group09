---
title: "状態ブロードキャスト（20Hz）"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["034_task_handshake.md"]
---

## 概要

ホスト側のゲーム状態（敵・タワー・拠点HPなど）を、20Hz（50msに1回）で全クライアントに送信する。

## 作業

- `NetServer.send_state(state: dict) -> None`：state メッセージを全クライアントに送信
- ホストのゲームループから50msに1回呼び出す（または送信スレッドで自動的に）
- `state` の中身は `032_task_message_schemas.md` の state スキーマに従う

## 完了条件

- クライアントが state メッセージを 20Hz 程度で受信できる
- パケット送信失敗時に例外で落ちない
