"""Genetic algorithm helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .neural_net import NeuralNet


@dataclass
class EvolutionManager:
    population_size: int = 12
    mutation_rate: float = 0.08
    input_size: int = 4
    hidden_size: int = 6
    output_size: int = 2
    population: list[NeuralNet] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.population:
            self.population = [
                NeuralNet(self.input_size, self.hidden_size, self.output_size)
                for _ in range(self.population_size)
            ]

    def mutate(self, net: NeuralNet) -> NeuralNet:
        child = net.copy()
        for weights in (child.w1, child.b1, child.w2, child.b2):
            mask = np.random.random(weights.shape) < self.mutation_rate
            weights[...] += mask * np.random.normal(0.0, 0.1, weights.shape)
        return child

    def next_generation(self, fitness: list[float]) -> list[NeuralNet]:
        if len(fitness) != len(self.population):
            raise ValueError("fitness length must match population length")

        order = np.argsort(fitness)[::-1]
        parent_count = max(1, len(order) // 3)
        parents = [self.population[index] for index in order[:parent_count]]
        self.population = [
            self.mutate(parents[i % len(parents)]) for i in range(self.population_size)
        ]
        return self.population
