---
title: "プレイヤー2（前線役）の操作実装"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "017_epic_solo_mode.md"
depends_on: ["018_task_solo_game.md"]
---

## 概要

プレイヤー2（前線役）の操作（WASD＋JKL）を実装する。

## 作業

- WASD：キャラ移動
- J：通常攻撃（前方に弾を撃つ）
- K：特殊スキル（クールタイム枠だけ、中身は担当④）
- L：タワー修理（近接時、リソース消費）
- Shift：ダッシュ

## 完了条件

- soloモードでWASDで前線役を操作できる
- Jキーで通常攻撃ができる
- Shiftで一時的に速くなる
