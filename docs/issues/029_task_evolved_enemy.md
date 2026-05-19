---
title: "evolution/evolved_enemy.py：NN搭載敵クラス"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["022_task_nn_forward.md", "013_task_base_enemy.md"]
---

## 概要

`BaseEnemy` を継承し、NNで動きを決定する敵クラスを実装する。

## 作業

- `evolution/evolved_enemy.py` に `EvolvedEnemy` クラスを実装
- `BaseEnemy` を継承
- 個別NNを保持
- `update()` 内で：
  1. 入力ベクトル（12次元）を構築
     - 自分のHP（正規化）
     - 拠点までの距離・方向
     - 近傍タワー3つの相対位置と種類
  2. NN推論で (vx, vy) を取得
  3. その方向に移動

### 構造例

```python
from core.base_enemy import BaseEnemy
from evolution.neural_net import NeuralNet
import numpy as np

class EvolvedEnemy(BaseEnemy):
    def __init__(self, pos, hp, nn: NeuralNet | None = None):
        super().__init__(pos, hp)
        self._nn = nn if nn is not None else NeuralNet()

    def update(self, fortress, towers) -> None:
        x = self._build_input_vector(fortress, towers)
        vx, vy = self._nn.forward(x)
        self._pos = (self._pos[0] + vx * self._speed, self._pos[1] + vy * self._speed)
```

## 完了条件

- soloモードに組み込んで EvolvedEnemy が出現する
- NNに従って動くことが視覚的に確認できる（直進ではなく、タワーを避ける動きが見える）
