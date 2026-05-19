---
title: "突然変異処理"
labels: ["task", "evolution"]
assignees: []
milestone: null
parent: "021_epic_evolution_ai.md"
depends_on: ["023_task_nn_weights.md"]
---

## 概要

NNの重みにガウスノイズを加える突然変異を実装する。確率5%程度（パラメータで変更可）で各重み要素を変異させる。

## 作業

`EvolutionManager` に以下のメソッドを追加：

- `mutate(nn: NeuralNet, rate: float | None = None, scale: float = 0.1) -> None`
  - `rate`：変異確率（デフォルトは `constants.GA_MUTATION_RATE`）
  - `scale`：ノイズの標準偏差

### 実装例

```python
def mutate(self, nn: NeuralNet, rate: float | None = None, scale: float = 0.1) -> None:
    """重みの各要素に確率 rate でガウスノイズを加算する。"""
    rate = rate if rate is not None else GA_MUTATION_RATE
    weights = nn.get_weights()
    new_weights = []
    for w in weights:
        noise = np.random.randn(*w.shape) * scale
        mask = np.random.rand(*w.shape) < rate
        new_weights.append(w + noise * mask)
    nn.set_weights(new_weights)
```

## 完了条件

- 変異後のNNの重みが元と微妙に異なる
- 変異率0で重みが変化しないことが確認できる
