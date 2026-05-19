---
title: "evolution/neural_net.py：NNクラスの骨格と forward 実装"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["006_task_init_files.md"]
---

## 概要

NumPy のみで実装する小規模ニューラルネットの骨格を作る。各敵が個別に保持するNN。

## 作業

- `evolution/neural_net.py` に `NeuralNet` クラスを実装
- ネットワーク構造：
  - 入力層：12ノード
  - 隠れ層：1〜2層、各8〜16ノード（tanh活性化）
  - 出力層：2ノード（vx, vy、tanhで -1〜+1）
- `__init__` でランダム初期化
- `forward(input_vec: np.ndarray) -> np.ndarray` 実装

### 入力12ノードの内訳

- 自分のHP（正規化）：1
- 拠点までの距離・方向（dx, dy）：2
- 近傍タワー3つの相対位置と種類（3×3=9）

### 例

```python
import numpy as np

class NeuralNet:
    """敵1体ごとに保持される小規模ニューラルネット。"""

    def __init__(self, input_size: int = 12, hidden_size: int = 16, output_size: int = 2) -> None:
        self._w1: np.ndarray = np.random.randn(input_size, hidden_size) * 0.5
        self._b1: np.ndarray = np.zeros(hidden_size)
        self._w2: np.ndarray = np.random.randn(hidden_size, output_size) * 0.5
        self._b2: np.ndarray = np.zeros(output_size)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """順伝播。-1〜+1 の2次元出力を返す。"""
        h = np.tanh(x @ self._w1 + self._b1)
        return np.tanh(h @ self._w2 + self._b2)
```

## 完了条件

- 12次元の入力に対して2次元の出力を返す
- 出力値が -1〜+1 の範囲に収まる
- 型ヒントとdocstringが付いている
