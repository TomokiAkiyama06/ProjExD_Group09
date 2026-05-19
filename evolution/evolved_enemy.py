"""Enemy controlled by a neural network."""

from __future__ import annotations

import numpy as np

try:
    from ..core.base_enemy import BaseEnemy
except ImportError:
    from core.base_enemy import BaseEnemy

from .neural_net import NeuralNet


class EvolvedEnemy(BaseEnemy):
    def __init__(self, brain: NeuralNet | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.brain = brain or NeuralNet(input_size=4, hidden_size=6, output_size=2)

    def decide(self, inputs: np.ndarray) -> np.ndarray:
        return self.brain.forward(inputs)
