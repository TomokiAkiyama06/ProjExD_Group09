"""Tests for evolution helpers."""

from __future__ import annotations

import numpy as np

from core.constants import (
    EVOLUTION_ELITE_RATE,
    EVOLUTION_TOURNAMENT_SIZE,
    FITNESS_DAMAGE_WEIGHT,
    FITNESS_DISTANCE_WEIGHT,
    FITNESS_SURVIVAL_WEIGHT,
    EVOLUTION_MUTATION_RATE,
)
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
    # b1/b2 に非ゼロ値を設定してバイアスのコピー漏れも検出できるようにする
    w1, b1, w2, b2 = net.get_weights()
    b1[:] = np.linspace(-0.5, 0.5, b1.shape[0])
    b2[:] = np.linspace(-0.3, 0.3, b2.shape[0])
    net.set_weights([w1, b1, w2, b2])

    input_vec = np.linspace(0.0, 1.0, DEFAULT_INPUT_SIZE)
    expected = net.forward(input_vec)

    copied_net = NeuralNet()
    weights = net.get_weights()
    copied_net.set_weights(weights)
    assert np.allclose(copied_net.forward(input_vec), expected)

    # set_weights が defensive copy: 渡した配列を変更してもコピー先は影響を受けない
    # w1[0, :] は input_vec[0]==0.0 に対応するため b1 を変更して確実に検出する
    weights[1][0] += 999.0
    assert np.allclose(copied_net.forward(input_vec), expected)

    # get_weights が defensive copy: 返された配列を変更しても元のNNは影響を受けない
    leaked = net.get_weights()
    leaked[1][0] += 999.0
    assert np.allclose(net.forward(input_vec), expected)


def test_neural_net_clone_keeps_independent_weights() -> None:
    net = NeuralNet()
    cloned_net = net.clone()
    original_weights = cloned_net.get_weights()

    # set_weightsによる配列差し替えでなくin-place変更で浅いコピーバグも検出する
    net.w1[0, 0] += 1.0
    net.b1[0] += 1.0
    net.w2[0, 0] += 1.0
    net.b2[0] += 1.0

    assert np.array_equal(cloned_net.w1, original_weights[0])
    assert np.array_equal(cloned_net.b1, original_weights[1])
    assert np.array_equal(cloned_net.w2, original_weights[2])
    assert np.array_equal(cloned_net.b2, original_weights[3])


def test_evolution_manager_uses_default_neural_net_shape() -> None:
    manager = EvolutionManager(population_size=2)
    assert manager.population[0].input_size == DEFAULT_INPUT_SIZE
    assert manager.population[0].output_size == DEFAULT_OUTPUT_SIZE


def test_evolution_manager_uses_default_mutation_rate() -> None:
    manager = EvolutionManager(population_size=1)
    assert EVOLUTION_MUTATION_RATE == 0.05
    assert manager.mutation_rate == EVOLUTION_MUTATION_RATE


def test_next_generation_keeps_population_size() -> None:
    manager = EvolutionManager(population_size=6)
    generation = manager.next_generation([1, 2, 3, 4, 5, 6])
    assert len(generation) == 6


def test_crossover_mixes_parent_weights() -> None:
    manager = EvolutionManager(population_size=1)
    parent_a = NeuralNet(input_size=2, hidden_size=2, output_size=2)
    parent_b = NeuralNet(input_size=2, hidden_size=2, output_size=2)
    parent_a.set_weights([np.zeros_like(weights) for weights in parent_a.get_weights()])
    parent_b.set_weights([np.ones_like(weights) for weights in parent_b.get_weights()])
    random_state = np.random.get_state()

    try:
        np.random.seed(0)
        child = manager.crossover(parent_a, parent_b)
    finally:
        np.random.set_state(random_state)

    child_weights = child.get_weights()
    assert all(np.all((weights == 0.0) | (weights == 1.0)) for weights in child_weights)
    assert any(np.any(weights == 0.0) for weights in child_weights)
    assert any(np.any(weights == 1.0) for weights in child_weights)


def test_crossover_keeps_parents_independent() -> None:
    manager = EvolutionManager(population_size=1)
    parent_a = NeuralNet(input_size=2, hidden_size=2, output_size=2)
    parent_b = NeuralNet(input_size=2, hidden_size=2, output_size=2)
    parent_a_weights = parent_a.get_weights()
    parent_b_weights = parent_b.get_weights()

    child = manager.crossover(parent_a, parent_b)
    child.w1[0, 0] += 100.0

    assert all(
        np.array_equal(before, after)
        for before, after in zip(parent_a_weights, parent_a.get_weights(), strict=True)
    )
    assert all(
        np.array_equal(before, after)
        for before, after in zip(parent_b_weights, parent_b.get_weights(), strict=True)
    )


def test_mutate_rate_zero_keeps_weights_unchanged() -> None:
    manager = EvolutionManager(population_size=1)
    net = NeuralNet()
    original_weights = net.get_weights()

    manager.mutate(net, rate=0.0)

    mutated_weights = net.get_weights()
    assert all(
        np.array_equal(before, after)
        for before, after in zip(original_weights, mutated_weights, strict=True)
    )


def test_mutate_rate_one_changes_weights() -> None:
    manager = EvolutionManager(population_size=1)
    net = NeuralNet()
    original_weights = net.get_weights()
    random_state = np.random.get_state()

    try:
        np.random.seed(0)
        manager.mutate(net, rate=1.0, scale=0.1)
    finally:
        np.random.set_state(random_state)

    mutated_weights = net.get_weights()
    assert any(
        not np.array_equal(before, after)
        for before, after in zip(original_weights, mutated_weights, strict=True)
    )


def test_calc_fitness_uses_enemy_record_values() -> None:
    manager = EvolutionManager(population_size=1)
    enemy_record = {
        "damage_dealt": 3,
        "survival_time": 20,
        "distance_improvement": 4,
    }
    expected = (
        enemy_record["damage_dealt"] * FITNESS_DAMAGE_WEIGHT
        + enemy_record["survival_time"] * FITNESS_SURVIVAL_WEIGHT
        + enemy_record["distance_improvement"] * FITNESS_DISTANCE_WEIGHT
    )
    assert manager.calc_fitness(enemy_record) == expected


def test_select_elites_returns_highest_fitness_individuals() -> None:
    manager = EvolutionManager(population_size=1)
    population = [NeuralNet() for _ in range(4)]
    fitness_list = [3.0, 10.0, 1.0, 7.0]

    elites = manager.select_elites(population, fitness_list, n_elite=2)

    assert elites == [population[1], population[3]]


def test_select_elites_uses_default_elite_rate() -> None:
    manager = EvolutionManager(population_size=1)
    population = [NeuralNet() for _ in range(10)]
    fitness_list = [float(index) for index in range(10)]
    expected_count = int(len(population) * EVOLUTION_ELITE_RATE)

    elites = manager.select_elites(population, fitness_list)

    assert len(elites) == expected_count
    assert elites[0] is population[-1]


def test_tournament_select_returns_best_candidate() -> None:
    manager = EvolutionManager(population_size=1)
    population = [NeuralNet() for _ in range(EVOLUTION_TOURNAMENT_SIZE)]
    fitness_list = [1.0, 8.0, 3.0]

    selected = manager.tournament_select(
        population,
        fitness_list,
        k=EVOLUTION_TOURNAMENT_SIZE,
    )

    assert selected is population[1]
