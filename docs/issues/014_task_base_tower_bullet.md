---
title: "core/base_tower.py + core/bullet.py：タワー＆弾の基底"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md", "013_task_base_enemy.md"]
---

## 概要

タワー基底クラスと弾クラスを実装する。派生クラス（炎・氷・雷・物理）は担当③が実装するため、基底では単発攻撃の最小実装にする。

## 作業

### `core/base_tower.py`

- `BaseTower` 基底クラス
- インスタンス変数：
  - `_pos`：座標
  - `_range`：射程
  - `_damage`：ダメージ
  - `_cooldown`：攻撃間隔
  - `_last_shot_tick`：最終発射時刻
- メソッド：
  - `find_target(enemies: list[BaseEnemy]) -> BaseEnemy | None`
  - `attack(target: BaseEnemy) -> Bullet | None`
  - `update(enemies: list[BaseEnemy]) -> list[Bullet]`
  - `draw(screen: pg.Surface) -> None`

### `core/bullet.py`

- `Bullet` クラス
- インスタンス変数：
  - `_pos`：座標
  - `_target`：対象敵
  - `_speed`：弾速
  - `_damage`：ダメージ
- メソッド：
  - `update() -> None`
  - `draw(screen: pg.Surface) -> None`
  - `check_hit() -> bool`

## 完了条件

- 1種類のタワーが射程内の敵を撃てる
- 弾が当たると敵のHPが減る
