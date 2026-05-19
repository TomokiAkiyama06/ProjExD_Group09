"""Simple NumPy neural network."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class NeuralNet:
    input_size: int
    hidden_size: int
    output_size: int

    def __post_init__(self) -> None:
        scale = 0.2
        self.w1 = np.random.randn(self.input_size, self.hidden_size) * scale
        self.b1 = np.zeros(self.hidden_size)
        self.w2 = np.random.randn(self.hidden_size, self.output_size) * scale
        self.b2 = np.zeros(self.output_size)

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        x = np.asarray(inputs, dtype=float)
        hidden = np.tanh(x @ self.w1 + self.b1)
        return np.tanh(hidden @ self.w2 + self.b2)

    def copy(self) -> "NeuralNet":
        clone = NeuralNet(self.input_size, self.hidden_size, self.output_size)
        clone.w1 = self.w1.copy()
        clone.b1 = self.b1.copy()
        clone.w2 = self.w2.copy()
        clone.b2 = self.b2.copy()
        return clone
