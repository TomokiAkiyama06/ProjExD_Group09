"""Evolution graph data helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvolutionGraph:
    fitness_history: list[float] = field(default_factory=list)

    def add_generation(self, best_fitness: float) -> None:
        self.fitness_history.append(best_fitness)
