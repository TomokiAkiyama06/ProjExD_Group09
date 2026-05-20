"""進化ループ駆動ドライバ。

`EvolutionManager` と `EvolutionGraph` を仲介し、SoloGame / HostGame の
ゲームループから以下のインタフェースだけで使えるようにする:

- `spawn_enemy(pos)`: `WaveManager.enemy_factory` に渡すスポーン関数。
  現世代の `population` から NN を順に取り出して `EvolvedEnemy` を返す。
- `finalize_wave(fortress_pos)`: ウェーブ終了時に呼び、戦績から fitness を
  計算 → `EvolutionManager.next_generation` → `EvolutionGraph.add` まで一括実行。
- `get_generation()`: HUD などから現在の世代番号を引くため。

`EvolutionGraph` は省略可能（Protocol 互換のものを受け取り、未指定なら何も
しない）。これにより `evolution` パッケージは `presentation` に runtime
依存しない。
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Protocol

from .evolution_manager import EvolutionManager
from .evolved_enemy import EvolvedEnemy
from .neural_net import NeuralNet


class GraphSink(Protocol):
    """`EvolutionGraph.add` を満たす最小プロトコル。"""

    def add(self, generation: int, best: float, avg: float) -> None:
        """世代の最高 / 平均適応度を追記する。"""


@dataclass
class _SpawnRecord:
    """戦績計算のためにスポーン時の情報を保持するエントリ。"""

    enemy: EvolvedEnemy
    brain: NeuralNet
    spawn_time: float
    initial_distance: float = 0.0


@dataclass
class EvolutionDriver:
    """SoloGame からの enemy_factory 兼、世代切替のドライバ。"""

    manager: EvolutionManager
    graph: GraphSink | None = None
    fortress_pos: tuple[float, float] = (0.0, 0.0)
    _spawn_index: int = 0
    _spawned: list[_SpawnRecord] = field(default_factory=list)
    _last_avg: float = 0.0
    _last_best: float = 0.0

    # ----- accessors -----

    def get_generation(self) -> int:
        """現在の世代番号を返す。"""
        return self.manager.get_generation()

    def get_last_best(self) -> float:
        """最後に計算した最高適応度を返す（HUD 用）。"""
        return self._last_best

    def get_last_avg(self) -> float:
        """最後に計算した平均適応度を返す（HUD 用）。"""
        return self._last_avg

    def get_spawned_count(self) -> int:
        """今ウェーブで spawn 済みの敵数を返す。"""
        return len(self._spawned)

    def set_fortress_pos(self, pos: tuple[float, float]) -> None:
        """拠点座標を設定する（finalize_wave での距離計算に使う）。"""
        self.fortress_pos = (float(pos[0]), float(pos[1]))

    # ----- spawn -----

    def spawn_enemy(self, pos: tuple[float, float]) -> EvolvedEnemy:
        """現世代の NN を 1 個体使って EvolvedEnemy を生成する。

        `WaveManager(enemy_factory=driver.spawn_enemy)` のように渡す想定。
        個体は population をラウンドロビンで巡回。
        """
        population = self.manager.population
        if not population:
            # フェイルセーフ：population が空なら新規 NN で生成
            brain = NeuralNet(
                input_size=self.manager.input_size,
                hidden_size=self.manager.hidden_size,
                output_size=self.manager.output_size,
            )
        else:
            brain = population[self._spawn_index % len(population)]
            self._spawn_index += 1

        enemy = EvolvedEnemy(
            pos=pos,
            brain=brain,
            generation=self.manager.get_generation(),
        )
        initial_distance = math.hypot(
            self.fortress_pos[0] - pos[0],
            self.fortress_pos[1] - pos[1],
        )
        self._spawned.append(
            _SpawnRecord(
                enemy=enemy,
                brain=brain,
                spawn_time=time.monotonic(),
                initial_distance=initial_distance,
            )
        )
        return enemy

    # ----- wave end -----

    def finalize_wave(self) -> bool:
        """ウェーブ終了時に呼び、fitness 計算 → next_generation → graph 追記。

        Returns:
            実際に世代が進んだ場合 True。前ウェーブでスポーンしていない場合は False。
        """
        if not self._spawned:
            return False

        best, avg, fitness_list = self._compute_fitness_per_population()
        previous_generation = self.manager.get_generation()
        self.manager.next_generation(fitness_list)
        self._last_best = best
        self._last_avg = avg
        if self.graph is not None:
            self.graph.add(previous_generation, best, avg)
        # ウェーブ計測のリセット
        self._spawned.clear()
        self._spawn_index = 0
        return True

    # ----- internal -----

    def _compute_fitness_per_population(self) -> tuple[float, float, list[float]]:
        """ウェーブで使われた NN ごとに fitness を集計し、population 順のリストにする。"""
        population_ids = [id(nn) for nn in self.manager.population]
        sums = [0.0] * len(population_ids)
        counts = [0] * len(population_ids)

        now = time.monotonic()
        for record in self._spawned:
            try:
                idx = population_ids.index(id(record.brain))
            except ValueError:
                # population が既に進化済みで brain が見つからない場合は無視
                continue
            fitness = self._calc_record_fitness(record, now)
            sums[idx] += fitness
            counts[idx] += 1

        fitness_list = [
            (sums[i] / counts[i]) if counts[i] > 0 else 0.0 for i in range(len(population_ids))
        ]
        best = max(fitness_list) if fitness_list else 0.0
        avg = sum(fitness_list) / len(fitness_list) if fitness_list else 0.0
        return best, avg, fitness_list

    def _calc_record_fitness(self, record: _SpawnRecord, now: float) -> float:
        """1 個体のスポーン記録から fitness を算出する。"""
        enemy = record.enemy
        damage_dealt = enemy.get_damage() if enemy.has_reached_fortress() else 0
        survival_time = max(0.0, now - record.spawn_time)
        ex, ey = enemy.get_pos()
        end_distance = math.hypot(self.fortress_pos[0] - ex, self.fortress_pos[1] - ey)
        distance_improvement = max(0.0, record.initial_distance - end_distance)
        return self.manager.calc_fitness(
            {
                "damage_dealt": int(damage_dealt),
                "survival_time": float(survival_time),
                "distance_improvement": float(distance_improvement),
            }
        )
