"""Tests for evolution helpers."""

from __future__ import annotations

import numpy as np

from evolution.evolution_manager import EvolutionManager
from evolution.neural_net import DEFAULT_INPUT_SIZE, DEFAULT_OUTPUT_SIZE, NeuralNet


def test_neural_net_forward_shape() -> None:
    net = NeuralNet()
    output = net.forward(np.zeros(DEFAULT_INPUT_SIZE))
    assert output.shape == (DEFAULT_OUTPUT_SIZE,)


def test_neural_net_forward_output_range() -> None:
    net = NeuralNet()
    output = net.forward(np.ones(DEFAULT_INPUT_SIZE))
    assert np.all((output >= -1.0) & (output <= 1.0))


def test_neural_net_rejects_wrong_input_shape() -> None:
    net = NeuralNet()
    try:
        net.forward(np.zeros(DEFAULT_INPUT_SIZE - 1))
    except ValueError as error:
        assert "input_vec must have shape" in str(error)
    else:
        raise AssertionError("NeuralNet.forward should reject wrong input shape")


def test_neural_net_set_weights_matches_forward_result() -> None:
    net = NeuralNet()
    copied_net = NeuralNet()
    copied_net.set_weights(net.get_weights())

    input_vec = np.linspace(0.0, 1.0, DEFAULT_INPUT_SIZE)
    assert np.allclose(copied_net.forward(input_vec), net.forward(input_vec))


def test_neural_net_clone_keeps_independent_weights() -> None:
    net = NeuralNet()
    cloned_net = net.clone()
    cloned_weights = cloned_net.get_weights()

    changed_weights = net.get_weights()
    changed_weights[0][0, 0] += 1.0
    net.set_weights(changed_weights)

    assert not np.array_equal(cloned_net.w1, net.w1)
    assert np.array_equal(cloned_net.w1, cloned_weights[0])


def test_evolution_manager_uses_default_neural_net_shape() -> None:
    manager = EvolutionManager(population_size=2)
    assert manager.population[0].input_size == DEFAULT_INPUT_SIZE
    assert manager.population[0].output_size == DEFAULT_OUTPUT_SIZE


def test_next_generation_keeps_population_size() -> None:
    manager = EvolutionManager(population_size=6)
    generation = manager.next_generation([1, 2, 3, 4, 5, 6])
    assert len(generation) == 6
