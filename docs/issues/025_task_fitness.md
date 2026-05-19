---
title: "evolution/evolution_manager.py：適応度計算"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

各敵個体の適応度（fitness）を計算する関数を実装する。生存時間や拠点到達状況などから「次世代に残すべき優秀さ」を数値化する。

## 作業

- `evolution/evolution_manager.py` に `EvolutionManager` クラスの骨格を作る
- 適応度計算メソッドを実装：

```
fitness = damage_dealt * 10 + survival_time * 1 + distance_improvement * 5
```

- `damage_dealt`：拠点に与えたダメージ
- `survival_time`：生存していたフレーム数
- `distance_improvement`：開始時から拠点までの最短到達距離の改善量

### メソッド例

```python
def calc_fitness(self, enemy_record: dict) -> float:
    """1個体の適応度を計算する。"""
    return (
        enemy_record["damage_dealt"] * 10.0
        + enemy_record["survival_time"] * 1.0
        + enemy_record["distance_improvement"] * 5.0
    )
```

## 完了条件

- 個体ごとの記録（dict）を渡すと適応度が数値で返ってくる
- パラメータ（係数）は `core/constants.py` から読む構造になっている
