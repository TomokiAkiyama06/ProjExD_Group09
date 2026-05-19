"""Tests for evolution helpers."""

from __future__ import annotations

import numpy as np

from .evolution_manager import EvolutionManager
from .neural_net import NeuralNet


def test_neural_net_forward_shape() -> None:
    net = NeuralNet(input_size=4, hidden_size=5, output_size=2)
    output = net.forward(np.zeros(4))
    assert output.shape == (2,)


def test_next_generation_keeps_population_size() -> None:
    manager = EvolutionManager(population_size=6)
    generation = manager.next_generation([1, 2, 3, 4, 5, 6])
    assert len(generation) == 6
