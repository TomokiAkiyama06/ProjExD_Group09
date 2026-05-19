---
title: "network/state_buffer.py：補間処理"
labels: ["task", "network"]
assignees: []
milestone: null
parent: "030_epic_network.md"
depends_on: ["035_task_state_broadcast.md"]
---

## 概要

20Hzで届く state を、クライアント側で線形補間して 60FPS で滑らかに描画する。

## 作業

- `network/state_buffer.py` に `StateBuffer` クラスを実装
- 機能：
  - `add(state: dict, recv_time: float) -> None`：受信時刻付きでstateを保存
  - `get_interpolated(now: float) -> dict`：直近2フレームの間で線形補間したstateを返す
- パケットロス時の挙動：
  - 直近stateをそのまま使う（簡易実装）
  - もしくは速度を維持して外挿（任意）

### 線形補間の擬似コード

```
t1, state1 = 直前の受信時刻と状態
t2, state2 = 最新の受信時刻と状態
alpha = (now - t1) / (t2 - t1)  # 0〜1
interpolated_pos = state1.pos + (state2.pos - state1.pos) * alpha
```

## 完了条件

- 20Hz受信でも敵の動きがカクつかず60FPSで滑らかに見える
