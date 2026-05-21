"""Tests for evolution helpers."""

from __future__ import annotations

import numpy as np

from core.base_tower import BaseTower
from core.constants import (
    EARLY_GENERATION_THRESHOLD,
    EVOLUTION_ELITE_RATE,
    EVOLUTION_TOURNAMENT_SIZE,
    FITNESS_DAMAGE_WEIGHT,
    FITNESS_DISTANCE_WEIGHT,
    FITNESS_SURVIVAL_WEIGHT,
    GA_MUTATION_RATE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from core.fortress import Fortress
from core.world import World
from evolution.evolution_driver import EvolutionDriver
from evolution.evolution_manager import EvolutionManager
from evolution.evolved_enemy import EvolvedEnemy
from evolution.neural_net import DEFAULT_INPUT_SIZE, DEFAULT_OUTPUT_SIZE, NeuralNet


class _CapturingEvolutionManager(EvolutionManager):
    """next_generation に渡された fitness を検証用に保持する manager。"""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.captured_fitness: list[float] | None = None

    def next_generation(self, fitness: list[float]) -> list[NeuralNet]:
        self.captured_fitness = list(fitness)
        return super().next_generation(fitness)


class _FixedBrain:
    def __init__(self, output: tuple[float, float]) -> None:
        self._output: np.ndarray = np.asarray(output, dtype=float)
        self.last_input: np.ndarray | None = None

    def forward(self, input_vec: np.ndarray) -> np.ndarray:
        self.last_input = np.asarray(input_vec, dtype=float)
        return self._output


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


def test_evolved_enemy_builds_twelve_dimensional_input() -> None:
    enemy = EvolvedEnemy(pos=(100.0, 100.0), hp=20)
    enemy.take_damage(5)
    fortress = Fortress(pos=(580.0, 370.0))
    tower = BaseTower(pos=(196.0, 154.0))

    input_vec = enemy._build_input_vector(fortress, [tower])

    assert input_vec.shape == (DEFAULT_INPUT_SIZE,)
    assert input_vec[0] == 0.75
    assert input_vec[1] == (fortress.get_pos()[0] - enemy.get_pos()[0]) / SCREEN_WIDTH
    assert input_vec[2] == (fortress.get_pos()[1] - enemy.get_pos()[1]) / SCREEN_HEIGHT
    assert input_vec[3] == (tower.get_pos()[0] - enemy.get_pos()[0]) / SCREEN_WIDTH
    assert input_vec[4] == (tower.get_pos()[1] - enemy.get_pos()[1]) / SCREEN_HEIGHT


def test_evolved_enemy_moves_with_brain_output() -> None:
    brain = _FixedBrain((1.0, 0.0))
    enemy = EvolvedEnemy(pos=(100.0, 100.0), brain=brain, speed=60.0)
    fortress = Fortress(pos=(900.0, 100.0))

    enemy.update_with_towers(fortress, [], dt=0.5)

    assert enemy.get_pos() == (130.0, 100.0)
    assert brain.last_input is not None


def test_world_passes_towers_to_evolved_enemy() -> None:
    brain = _FixedBrain((0.0, 1.0))
    # EARLY_GENERATION_THRESHOLD を超えた世代を指定してNNパスを通す
    enemy = EvolvedEnemy(
        pos=(100.0, 100.0),
        brain=brain,
        speed=0.0,
        generation=EARLY_GENERATION_THRESHOLD + 1,
    )
    tower = BaseTower(pos=(220.0, 160.0))
    world = World(spawn_points=[], fortress=Fortress(pos=(900.0, 100.0)))
    world.add_enemy(enemy)
    world.add_tower(tower)

    world.update(0.1)

    assert brain.last_input is not None
    assert brain.last_input[3] == (tower.get_pos()[0] - enemy.get_pos()[0]) / SCREEN_WIDTH
    assert brain.last_input[4] == (tower.get_pos()[1] - enemy.get_pos()[1]) / SCREEN_HEIGHT


def test_early_generation_moves_toward_nearest_tower() -> None:
    """初期世代（閾値以下）はNNを使わず最近傍タワーへ向かうことを確認する。"""
    brain = _FixedBrain((0.0, 0.0))  # NN出力は原点（呼ばれないはず）
    enemy = EvolvedEnemy(
        pos=(100.0, 300.0),
        brain=brain,
        speed=60.0,
        generation=EARLY_GENERATION_THRESHOLD,
    )
    tower = BaseTower(pos=(200.0, 300.0))  # 真横にタワー
    fortress = Fortress(pos=(900.0, 300.0))

    enemy.update_with_towers(fortress, [tower], dt=1.0)

    ex, ey = enemy.get_pos()
    assert ex > 100.0, "タワー方向（+x）に移動しているはず"
    assert abs(ey - 300.0) < 1e-9, "y座標は変わらないはず"
    assert brain.last_input is None, "早期世代ではNNは呼ばれないはず"


def test_early_generation_falls_back_to_nn_when_no_towers() -> None:
    """初期世代でもタワーがなければNNで移動することを確認する。"""
    brain = _FixedBrain((1.0, 0.0))
    enemy = EvolvedEnemy(
        pos=(100.0, 100.0),
        brain=brain,
        speed=60.0,
        generation=0,
    )
    fortress = Fortress(pos=(900.0, 100.0))

    enemy.update_with_towers(fortress, [], dt=0.5)

    assert enemy.get_pos() == (130.0, 100.0)
    assert brain.last_input is not None, "タワーなし時はNNにフォールバックするはず"


def test_later_generation_uses_nn_even_with_towers() -> None:
    """閾値を超えた世代はタワーがあってもNNを使うことを確認する。"""
    brain = _FixedBrain((0.0, 1.0))  # 真下に移動するNN出力
    enemy = EvolvedEnemy(
        pos=(100.0, 100.0),
        brain=brain,
        speed=60.0,
        generation=EARLY_GENERATION_THRESHOLD + 1,
    )
    tower = BaseTower(pos=(200.0, 100.0))  # 真横にタワー
    fortress = Fortress(pos=(900.0, 100.0))

    enemy.update_with_towers(fortress, [tower], dt=0.5)

    _ex, ey = enemy.get_pos()
    assert ey > 100.0, "NNの出力（+y方向）に移動しているはず"
    assert brain.last_input is not None, "閾値超えではNNが呼ばれるはず"


def test_evolution_manager_uses_default_neural_net_shape() -> None:
    manager = EvolutionManager(population_size=2)
    assert manager.population[0].input_size == DEFAULT_INPUT_SIZE
    assert manager.population[0].output_size == DEFAULT_OUTPUT_SIZE


def test_evolution_manager_uses_default_mutation_rate() -> None:
    manager = EvolutionManager(population_size=1)
    assert manager.mutation_rate == GA_MUTATION_RATE


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


def test_evolution_driver_waits_until_population_is_evaluated() -> None:
    manager = EvolutionManager(population_size=3)
    now = 0.0
    driver = EvolutionDriver(manager=manager, time_source=lambda: now)

    driver.spawn_enemy((100.0, 100.0))
    driver.spawn_enemy((100.0, 100.0))

    assert not driver.finalize_wave()
    assert manager.get_generation() == 1
    assert driver.get_evaluated_population_count() == 2
    assert driver.get_spawned_count() == 0

    driver.spawn_enemy((100.0, 100.0))

    assert driver.finalize_wave()
    assert manager.get_generation() == 2
    assert driver.get_evaluated_population_count() == 0
    assert driver.get_spawned_count() == 0


def test_evolution_driver_uses_locked_survival_time_for_dead_enemy() -> None:
    now = 0.0

    def current_time() -> float:
        return now

    manager = _CapturingEvolutionManager(population_size=2)
    driver = EvolutionDriver(manager=manager, time_source=current_time)
    early = driver.spawn_enemy((100.0, 100.0))
    driver.spawn_enemy((100.0, 100.0))

    now = 0.5
    early.take_damage(early.get_hp())
    driver.observe_frame()

    now = 5.0
    assert driver.finalize_wave()

    assert manager.captured_fitness is not None
    assert manager.captured_fitness[0] < manager.captured_fitness[1]
