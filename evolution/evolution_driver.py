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
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from core.constants import ENEMY_HP_GROWTH_PER_GENERATION

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
    # 死亡または拠点到達した瞬間のタイムスタンプ。生存中は None。
    end_time: float | None = None
    # 終了時点の座標（敵が World から取り除かれた後でも distance_improvement を
    # 計算できるよう、死亡/到達フレームで確定させる）。
    end_pos: tuple[float, float] | None = None


@dataclass
class EvolutionDriver:
    """SoloGame からの enemy_factory 兼、世代切替のドライバ。"""

    manager: EvolutionManager
    graph: GraphSink | None = None
    fortress_pos: tuple[float, float] = (0.0, 0.0)
    time_source: Callable[[], float] = time.monotonic
    _spawn_index: int = 0
    _spawned: list[_SpawnRecord] = field(default_factory=list)
    _fitness_sums: list[float] = field(default_factory=list)
    _fitness_counts: list[int] = field(default_factory=list)
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

    def get_evaluated_population_count(self) -> int:
        """現世代で少なくとも 1 回 fitness を得た個体数を返す。"""
        self._ensure_fitness_buffers()
        return sum(1 for count in self._fitness_counts if count > 0)

    def set_fortress_pos(self, pos: tuple[float, float]) -> None:
        """拠点座標を設定する（finalize_wave での距離計算に使う）。"""
        self.fortress_pos = (float(pos[0]), float(pos[1]))

    # ----- per-frame observation -----

    def observe_frame(self, now: float | None = None) -> None:
        """SoloGame の毎フレームで呼び、死亡/到達した個体の終了時刻を確定する。

        敵が World._enemies から外される前後どちらでも、`enemy.is_dead()` または
        `enemy.has_reached_fortress()` が True になった瞬間の `now` をその個体の
        終了タイムスタンプとして記録する。
        """
        if now is None:
            now = self.time_source()
        for record in self._spawned:
            if record.end_time is not None:
                continue
            enemy = record.enemy
            if enemy.is_dead() or enemy.has_reached_fortress():
                record.end_time = now
                record.end_pos = enemy.get_pos()

    # ----- spawn -----

    def _hp_factor(self) -> float:
        """現世代に応じた敵 HP 倍率を返す（世代1 で 1.0）。

        同一世代内では一定値となるため、population を複数ウェーブにまたがって
        round-robin 評価しても個体ごとに HP が変わらず、fitness 比較の公平性
        （ウェーブ依存スケーリングによる選択バイアス）を回避できる。
        """
        generation = self.manager.get_generation()
        return 1.0 + ENEMY_HP_GROWTH_PER_GENERATION * max(0, generation - 1)

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
        # 世代単位の HP スケーリング（同一世代内は一定 → fitness 比較が公平）
        enemy.scale_hp(self._hp_factor())
        initial_distance = math.hypot(
            self.fortress_pos[0] - pos[0],
            self.fortress_pos[1] - pos[1],
        )
        self._spawned.append(
            _SpawnRecord(
                enemy=enemy,
                brain=brain,
                spawn_time=self.time_source(),
                initial_distance=initial_distance,
            )
        )
        return enemy

    # ----- wave end -----

    def finalize_wave(self) -> bool:
        """ウェーブ終了時に呼び、fitness 計算 → next_generation → graph 追記。

        Returns:
            実際に世代が進んだ場合 True。前ウェーブでスポーンしていない場合は False。
            現世代の未評価個体が残っている場合も False を返し、評価を次ウェーブへ
            持ち越す。
        """
        if not self._spawned:
            return False

        now = self.time_source()
        self._close_wave_records(now)
        self._accumulate_spawned_fitness(now)
        self._spawned.clear()

        if not self._has_evaluated_full_population():
            self._update_last_fitness_from_accumulated()
            return False

        best, avg, fitness_list = self._compute_fitness_per_population()
        previous_generation = self.manager.get_generation()
        self.manager.next_generation(fitness_list)
        self._last_best = best
        self._last_avg = avg
        if self.graph is not None:
            self.graph.add(previous_generation, best, avg)
        # ウェーブ計測のリセット
        self._spawn_index = 0
        self._fitness_sums.clear()
        self._fitness_counts.clear()
        return True

    # ----- internal -----

    def _compute_fitness_per_population(self) -> tuple[float, float, list[float]]:
        """現世代の評価済み fitness を population 順のリストにする。"""
        self._ensure_fitness_buffers()
        fitness_list = [
            self._fitness_sums[i] / self._fitness_counts[i]
            for i in range(len(self._fitness_counts))
        ]
        best = max(fitness_list) if fitness_list else 0.0
        avg = sum(fitness_list) / len(fitness_list) if fitness_list else 0.0
        return best, avg, fitness_list

    def _ensure_fitness_buffers(self) -> None:
        """現 population サイズに合わせて fitness 蓄積バッファを用意する。"""
        population_size = len(self.manager.population)
        if len(self._fitness_sums) == population_size:
            return
        self._fitness_sums = [0.0] * population_size
        self._fitness_counts = [0] * population_size

    def _close_wave_records(self, now: float) -> None:
        """Finalize 時点で生存中の個体にも終了時刻と座標を記録する。"""
        self.observe_frame(now=now)
        for record in self._spawned:
            if record.end_time is None:
                record.end_time = now
                record.end_pos = record.enemy.get_pos()

    def _accumulate_spawned_fitness(self, now: float) -> None:
        """このウェーブで spawn された個体の fitness を現世代の蓄積値へ加える。"""
        self._ensure_fitness_buffers()
        population_ids = [id(nn) for nn in self.manager.population]
        for record in self._spawned:
            try:
                idx = population_ids.index(id(record.brain))
            except ValueError:
                # population が既に進化済みで brain が見つからない場合は無視
                continue
            fitness = self._calc_record_fitness(record, now)
            self._fitness_sums[idx] += fitness
            self._fitness_counts[idx] += 1

    def _has_evaluated_full_population(self) -> bool:
        """現世代の全個体が少なくとも 1 回評価済みなら True。"""
        self._ensure_fitness_buffers()
        return bool(self._fitness_counts) and all(count > 0 for count in self._fitness_counts)

    def _update_last_fitness_from_accumulated(self) -> None:
        """未評価個体が残る間も HUD 用の直近 best/avg を評価済み分から更新する。"""
        fitness_values = [
            fitness_sum / count
            for fitness_sum, count in zip(
                self._fitness_sums,
                self._fitness_counts,
                strict=True,
            )
            if count > 0
        ]
        self._last_best = max(fitness_values) if fitness_values else 0.0
        self._last_avg = sum(fitness_values) / len(fitness_values) if fitness_values else 0.0

    def _calc_record_fitness(self, record: _SpawnRecord, now: float) -> float:
        """1 個体のスポーン記録から fitness を算出する。

        死亡/到達済みの個体は `record.end_time` を使い、生存個体は `now` を使う。
        これにより早期に倒された敵にウェーブ終了までの時間が加算されない。
        """
        enemy = record.enemy
        damage_dealt = enemy.get_damage() if enemy.has_reached_fortress() else 0
        end_time = record.end_time if record.end_time is not None else now
        survival_time = max(0.0, end_time - record.spawn_time)
        # 終了座標も確定済みならそれを使う（敵が World から除外された後でも安全）。
        ex, ey = record.end_pos if record.end_pos is not None else enemy.get_pos()
        end_distance = math.hypot(self.fortress_pos[0] - ex, self.fortress_pos[1] - ey)
        distance_improvement = max(0.0, record.initial_distance - end_distance)
        return self.manager.calc_fitness(
            {
                "damage_dealt": int(damage_dealt),
                "survival_time": float(survival_time),
                "distance_improvement": float(distance_improvement),
            }
        )
