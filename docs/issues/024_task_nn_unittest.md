---
title: "NNの単体テスト作成"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["022_task_nn_forward.md", "023_task_nn_weights.md"]
---

## 概要

`NeuralNet` クラスの単体テストを作成する。外部ライブラリ不要のシンプルなassert形式。

## 作業

- `evolution/test_evolution.py` を作成
- テスト項目：
  - `test_forward_shape`：12次元入力で2次元出力が返るか
  - `test_forward_range`：出力値が -1〜+1 の範囲か
  - `test_weights_roundtrip`：`get_weights` → `set_weights` で同じ forward 結果になるか
  - `test_clone_independence`：`clone()` 後に元を変更してもコピーに影響しないか

### 実行方法

```bash
python -m evolution.test_evolution
```

### 例

```python
import numpy as np
from evolution.neural_net import NeuralNet

def test_forward_shape() -> None:
    nn = NeuralNet()
    out = nn.forward(np.zeros(12))
    assert out.shape == (2,)
    print("[OK] test_forward_shape")

if __name__ == "__main__":
    test_forward_shape()
    print("All tests passed.")
```

## 完了条件

- `python -m evolution.test_evolution` で全テストがパスする
