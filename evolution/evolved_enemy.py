"""Enemy controlled by a neural network."""

from __future__ import annotations

import numpy as np

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy

from .neural_net import NeuralNet


class EvolvedEnemy(BaseEnemy):
    """ニューラルネットで移動方向を判断する敵。"""

    def __init__(self, brain: NeuralNet | None = None, **kwargs: object) -> None:
        """敵を初期化し、未指定なら標準構成のNNを割り当てる。"""
        super().__init__(**kwargs)
        self._brain: NeuralNet = brain or NeuralNet()

    @property
    def brain(self) -> NeuralNet:
        """敵が保持するニューラルネットを返す。"""
        return self._brain

    def decide(self, inputs: np.ndarray) -> np.ndarray:
        """現在の観測入力から移動方向ベクトルを決定する。"""
        return self.brain.forward(inputs)
