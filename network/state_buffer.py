"""20Hz で届く state を 60FPS で滑らかに描画するための補間バッファ。

`get_interpolated(now)` で直近 2 state の間を線形補間した state を返す。
位置のみ補間し、それ以外は最新の state をそのまま使う（id でエンティティ
を対応付ける）。

簡易仕様:
    - `push(timestamp, state)` で受信時刻付きで保存（時刻昇順を維持）。
    - `latest()` で最新 state のみ返す。
    - `get_interpolated(now)` は now を挟む 2 state を選び、`enemies` /
      `towers` / `players` 等の各リスト内エンティティを `id` で対応付け、
      `pos` を線形補間する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 補間対象になる「リスト・オブ・dict」のキー
_INTERPOLATABLE_LISTS: tuple[str, ...] = ("enemies", "towers", "players", "bullets")


@dataclass
class StateBuffer:
    """受信した state を時刻順に保持し補間する。"""

    max_size: int = 60
    states: list[tuple[float, dict[str, Any]]] = field(default_factory=list)

    # ----- mutators -----

    def push(self, timestamp: float, state: dict[str, Any]) -> None:
        """時刻付きで state を追加する（時刻昇順でソート）。"""
        self.states.append((float(timestamp), state))
        self.states.sort(key=lambda item: item[0])
        if len(self.states) > self.max_size:
            self.states = self.states[-self.max_size :]

    def add(self, state: dict[str, Any], recv_time: float) -> None:
        """タスク #40 の仕様 API。push の別名（引数順が異なる）。"""
        self.push(recv_time, state)

    def clear(self) -> None:
        self.states.clear()

    # ----- accessors -----

    def latest(self) -> dict[str, Any] | None:
        if not self.states:
            return None
        return self.states[-1][1]

    def latest_timestamp(self) -> float | None:
        if not self.states:
            return None
        return self.states[-1][0]

    def get_interpolated(  # noqa: PLR0911 - 端ケース（0件/1件/最古/最新）の early return を維持
        self,
        now: float,
    ) -> dict[str, Any] | None:
        """Now の時点での補間 state を返す。

        - 受信が 0 件: None
        - 受信が 1 件: その state をそのまま返す
        - now が最古以前 or 最新以後: 端の state を返す（外挿はしない）
        - now が 2 state の間: alpha = (now - t1)/(t2 - t1) で `pos` を線形補間
        """
        if not self.states:
            return None
        if len(self.states) == 1:
            return self.states[0][1]

        t_first = self.states[0][0]
        t_last = self.states[-1][0]
        if now <= t_first:
            return self.states[0][1]
        if now >= t_last:
            return self.states[-1][1]

        # now を挟むペアを探す
        prev = self.states[0]
        for nxt in self.states[1:]:
            if prev[0] <= now <= nxt[0]:
                if nxt[0] == prev[0]:
                    return nxt[1]
                alpha = (now - prev[0]) / (nxt[0] - prev[0])
                return _interpolate_state(prev[1], nxt[1], alpha)
            prev = nxt
        return self.states[-1][1]


def _interpolate_state(
    earlier: dict[str, Any],
    later: dict[str, Any],
    alpha: float,
) -> dict[str, Any]:
    """位置を補間した中間 state を作る。基本値は later を踏襲する。"""
    alpha = max(0.0, min(1.0, float(alpha)))
    result: dict[str, Any] = dict(later)
    for key in _INTERPOLATABLE_LISTS:
        earlier_list = earlier.get(key)
        later_list = later.get(key)
        if not isinstance(earlier_list, list) or not isinstance(later_list, list):
            continue
        earlier_by_id = {item.get("id"): item for item in earlier_list if isinstance(item, dict)}
        merged: list[dict[str, Any]] = []
        for item in later_list:
            if not isinstance(item, dict):
                merged.append(item)
                continue
            ident = item.get("id")
            prev_item = earlier_by_id.get(ident)
            if prev_item is None:
                merged.append(item)
                continue
            merged.append(_blend_entity(prev_item, item, alpha))
        result[key] = merged
    return result


def _blend_entity(
    prev_item: dict[str, Any],
    new_item: dict[str, Any],
    alpha: float,
) -> dict[str, Any]:
    """1 つのエンティティの pos を線形補間する。それ以外のフィールドは new_item を採用。"""
    blended = dict(new_item)
    prev_pos = prev_item.get("pos")
    next_pos = new_item.get("pos")
    if (
        isinstance(prev_pos, (list, tuple))
        and isinstance(next_pos, (list, tuple))
        and len(prev_pos) == len(next_pos)
    ):
        blended["pos"] = [
            float(p) + (float(n) - float(p)) * alpha
            for p, n in zip(prev_pos, next_pos, strict=True)
        ]
    return blended
