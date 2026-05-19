---
title: "交叉処理（一様交叉）"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["023_task_nn_weights.md", "026_task_selection.md"]
---

## 概要

親2体のNNから子1体のNNを作る一様交叉を実装する。各重み要素を50%確率でどちらかの親から引き継ぐ。

## 作業

`EvolutionManager` に以下のメソッドを追加：

- `crossover(parent_a: NeuralNet, parent_b: NeuralNet) -> NeuralNet`

### 実装例

```python
def crossover(self, parent_a: NeuralNet, parent_b: NeuralNet) -> NeuralNet:
    """一様交叉。各要素を50%確率で親A or 親Bから受け継ぐ。"""
    child = parent_a.clone()
    wa = parent_a.get_weights()
    wb = parent_b.get_weights()
    new_weights = []
    for a, b in zip(wa, wb):
        mask = np.random.rand(*a.shape) < 0.5
        new_weights.append(np.where(mask, a, b))
    child.set_weights(new_weights)
    return child
```

## 完了条件

- 親2体から子1体を作れる
- 子の重みが両親の混合になっている（単純なコピーではない）
