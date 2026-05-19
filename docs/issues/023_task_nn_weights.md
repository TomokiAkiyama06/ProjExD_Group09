---
title: "NNの重み取得・設定メソッド（交叉用）"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["022_task_nn_forward.md"]
---

## 概要

遺伝的アルゴリズムの交叉処理で、親NNから子NNへ重みをコピーできるよう、重みの取り出し・設定機能を追加する。

## 作業

`NeuralNet` クラスに以下のメソッドを追加：

- `get_weights() -> list[np.ndarray]`：全重みをリストで返す
- `set_weights(weights: list[np.ndarray]) -> None`：全重みを上書き
- `clone() -> NeuralNet`：自身のコピー（独立した重みを持つNN）を返す

### 例

```python
def get_weights(self) -> list[np.ndarray]:
    return [self._w1.copy(), self._b1.copy(), self._w2.copy(), self._b2.copy()]

def set_weights(self, weights: list[np.ndarray]) -> None:
    self._w1, self._b1, self._w2, self._b2 = [w.copy() for w in weights]

def clone(self) -> "NeuralNet":
    new = NeuralNet()
    new.set_weights(self.get_weights())
    return new
```

## 完了条件

- 重みを取り出して別のNNに設定でき、forward結果が一致する
- `clone()` で独立したコピーができる（元を変更してもコピーに影響しない）
