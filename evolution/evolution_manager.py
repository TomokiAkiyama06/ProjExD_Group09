"""Genetic algorithm helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

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
