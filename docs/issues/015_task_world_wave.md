---
title: "core/world.py + core/wave_manager.py：マップとウェーブ管理"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["013_task_base_enemy.md"]
---

## 概要

マップ（背景・出現口）と、ウェーブ進行を管理するクラスを実装する。

## 作業

### `core/world.py`

- `World` クラス
- マップ背景の描画
- 敵の出現口の座標を保持
- タワー設置可能エリアの判定（タワー同士の重なり禁止など）

### `core/wave_manager.py`

- `WaveManager` クラス
- ウェーブごとの敵スポーン処理
- フェーズ管理：準備 → 戦闘 → 集計
- 現在のウェーブ番号を保持
- スポーン数や敵タイプはウェーブ番号に応じて変化

## 完了条件

- ウェーブ1〜3が順番に進む
- 各ウェーブで敵が出現口から出現する
- 全敵が倒されるとウェーブ終了 → 次のウェーブへ
