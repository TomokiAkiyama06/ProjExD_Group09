"""Genetic algorithm helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from core.constants import (
    EVOLUTION_ELITE_RATE,
    EVOLUTION_TOURNAMENT_SIZE,
    FITNESS_DAMAGE_WEIGHT,
    FITNESS_DISTANCE_WEIGHT,
    FITNESS_SURVIVAL_WEIGHT,
)

from .neural_net import DEFAULT_HIDDEN_SIZE, DEFAULT_INPUT_SIZE, DEFAULT_OUTPUT_SIZE, NeuralNet


@dataclass
class EvolutionManager:
    """ニューラルネット個体群を管理する簡易進化マネージャ。"""

    population_size: int = 12
    mutation_rate: float = 0.08
    input_size: int = DEFAULT_INPUT_SIZE
    hidden_size: int = DEFAULT_HIDDEN_SIZE
    output_size: int = DEFAULT_OUTPUT_SIZE
    population: list[NeuralNet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """初期個体群が未指定ならランダムなNN個体群を生成する。"""
        if not self.population:
            self.population = [
                NeuralNet(self.input_size, self.hidden_size, self.output_size)
                for _ in range(self.population_size)
            ]

    def mutate(self, net: NeuralNet) -> NeuralNet:
        """指定したNN個体をコピーし、一定確率で重みを変異させる。"""
        child = net.copy()
        for weights in (child.w1, child.b1, child.w2, child.b2):
            mask = np.random.random(weights.shape) < self.mutation_rate
            weights[...] += mask * np.random.normal(0.0, 0.1, weights.shape)
        return child

    def calc_fitness(self, enemy_record: dict[str, float | int]) -> float:
        """1個体の記録から適応度を計算する。

        Args:
            enemy_record: 敵1体の戦績。``damage_dealt``、``survival_time``、
                ``distance_improvement`` を含む辞書

        Returns:
            ダメージ・生存時間・距離改善量を重み付き合算した適応度
        """
        damage_dealt = float(enemy_record["damage_dealt"])
        survival_time = float(enemy_record["survival_time"])
        distance_improvement = float(enemy_record["distance_improvement"])
        return (
            damage_dealt * FITNESS_DAMAGE_WEIGHT
            + survival_time * FITNESS_SURVIVAL_WEIGHT
            + distance_improvement * FITNESS_DISTANCE_WEIGHT
        )

    def select_elites(
        self,
        population: list[NeuralNet],
        fitness_list: list[float],
        n_elite: int | None = None,
    ) -> list[NeuralNet]:
        """適応度が高い上位個体をエリートとして返す。

        Args:
            population: 選択対象のNN個体群
            fitness_list: 各個体に対応する適応度
            n_elite: 返すエリート数。未指定なら定数の割合から計算する

        Returns:
            適応度降順で並んだエリート個体のリスト

        Raises:
            ValueError: 個体群と適応度の長さが一致しない場合
        """
        self._validate_selection_inputs(population, fitness_list)
        elite_count = n_elite
        if elite_count is None:
            elite_count = int(len(population) * EVOLUTION_ELITE_RATE)
        elite_count = max(0, min(elite_count, len(population)))

        order = np.argsort(fitness_list)[::-1]
        return [population[index] for index in order[:elite_count]]

    def tournament_select(
        self,
        population: list[NeuralNet],
        fitness_list: list[float],
        k: int = EVOLUTION_TOURNAMENT_SIZE,
    ) -> NeuralNet:
        """ランダムに抽出した候補の中で最も適応度が高い個体を返す。

        Args:
            population: 選択対象のNN個体群
            fitness_list: 各個体に対応する適応度
            k: トーナメントに参加させる個体数

        Returns:
            抽出候補の中で最高適応度の個体

        Raises:
            ValueError: 個体群と適応度の長さが一致しない場合、またはkが1未満の場合
        """
        self._validate_selection_inputs(population, fitness_list)
        if k < 1:
            raise ValueError("k must be greater than 0")

        tournament_size = min(k, len(population))
        candidate_indexes = np.random.choice(
            len(population),
            size=tournament_size,
            replace=False,
        )
        best_index = max(candidate_indexes, key=lambda index: fitness_list[int(index)])
        return population[int(best_index)]

    def next_generation(self, fitness: list[float]) -> list[NeuralNet]:
        """適応度の高い個体を親として次世代を生成する。"""
        if len(fitness) != len(self.population):
            raise ValueError("fitness length must match population length")

        order = np.argsort(fitness)[::-1]
        parent_count = max(1, len(order) // 3)
        parents = [self.population[index] for index in order[:parent_count]]
        self.population = [
            self.mutate(parents[i % len(parents)]) for i in range(self.population_size)
        ]
        return self.population

    @staticmethod
    def _validate_selection_inputs(
        population: list[NeuralNet],
        fitness_list: list[float],
    ) -> None:
        """選択処理に使う個体群と適応度リストを検証する。"""
        if not population:
            raise ValueError("population must not be empty")
        if len(population) != len(fitness_list):
            raise ValueError("fitness_list length must match population length")
