"""Tests for evolution helpers."""

from __future__ import annotations

import numpy as np

from evolution.evolution_manager import EvolutionManager
from evolution.neural_net import NeuralNet


def test_neural_net_forward_shape() -> None:
    net = NeuralNet()
    output = net.forward(np.zeros(12))
    assert output.shape == (2,)


def test_neural_net_forward_output_range() -> None:
    net = NeuralNet()
    output = net.forward(np.ones(12))
    assert np.all((output >= -1.0) & (output <= 1.0))


def test_neural_net_rejects_wrong_input_shape() -> None:
    net = NeuralNet()
    try:
        net.forward(np.zeros(11))
    except ValueError as error:
        assert "input_vec must have shape" in str(error)
    else:
        raise AssertionError("NeuralNet.forward should reject wrong input shape")


def test_evolution_manager_uses_default_neural_net_shape() -> None:
    manager = EvolutionManager(population_size=2)
    assert manager.population[0].input_size == 12
    assert manager.population[0].output_size == 2


def test_next_generation_keeps_population_size() -> None:
    manager = EvolutionManager(population_size=6)
    generation = manager.next_generation([1, 2, 3, 4, 5, 6])
    assert len(generation) == 6
