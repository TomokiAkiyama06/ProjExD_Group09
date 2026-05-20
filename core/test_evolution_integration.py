"""SoloGame に進化AIが組み込まれていることの統合テスト。

- EvolutionDriver.spawn_enemy で EvolvedEnemy が World に投入される
- WaveManager の BATTLE → SUMMARY 遷移で EvolutionDriver.finalize_wave() が呼ばれる
- 世代が進む（manager.get_generation が +1 される、SoloGame._generation も追従）
- EvolutionGraph に世代記録が追記される
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

from core.solo_game import SoloGame
from core.wave_manager import WavePhase
from evolution.evolution_driver import EvolutionDriver
from evolution.evolution_manager import EvolutionManager
from evolution.evolved_enemy import EvolvedEnemy
from presentation.evolution_graph import EvolutionGraph


def _make_solo_game(graph: EvolutionGraph | None = None) -> SoloGame:
    """Driver/Graph 注入済みの SoloGame を作る共通ヘルパ。"""
    pg.init()
    pg.display.set_mode((400, 200))
    manager = EvolutionManager(population_size=4)
    driver = EvolutionDriver(manager=manager, graph=graph)
    return SoloGame(
        evolution_driver=driver,
        evolution_graph=graph,
        max_wave=2,
    )


def test_solo_game_uses_driver_as_enemy_factory() -> None:
    """SoloGame が EvolutionDriver.spawn_enemy を enemy_factory として使う。"""
    game = _make_solo_game()
    try:
        # PREPARE をスキップして BATTLE に
        game.get_builder()._wave_skip_requested = True  # 内部 API: 簡易テスト用
        for _ in range(2):
            game.update(1.0 / 60.0)
        # スポーン1体目を待つ（spawn 間隔 0.8s）
        for _ in range(int(1.0 * 60)):
            game.update(1.0 / 60.0)
            if game.get_world().get_enemies():
                break
        enemies = game.get_world().get_enemies()
        assert enemies, "1秒以上経過しても敵がスポーンしない"
        # 全敵が EvolvedEnemy であること
        assert all(isinstance(e, EvolvedEnemy) for e in enemies)
        # generation スタンプが第1世代であること
        assert all(e.get_generation() == 1 for e in enemies)
    finally:
        pg.quit()


def test_generation_progresses_after_wave_summary() -> None:
    """BATTLE → SUMMARY 遷移で世代が進み SoloGame._generation も更新される。"""
    game = _make_solo_game()
    driver = game._evolution_driver
    assert driver is not None
    try:
        assert driver.get_generation() == 1
        assert game._generation == 1
        # 強制的に SUMMARY フェーズに遷移したことにする
        # （実機ではウェーブ完走待ちだが、テストでは内部状態を直接書き換える）
        game._prev_wave_phase = WavePhase.BATTLE
        # ドライバに 1 体スポーン記録を入れて finalize_wave が空振りしないようにする
        driver.spawn_enemy((100.0, 100.0))
        game._wave_manager._phase = WavePhase.SUMMARY
        game._tick_evolution()
        assert driver.get_generation() == 2
        assert game._generation == 2
    finally:
        pg.quit()


def test_finalize_wave_appends_to_evolution_graph() -> None:
    """finalize_wave 経由で EvolutionGraph.add が呼ばれて履歴が増える。"""
    graph = EvolutionGraph()
    game = _make_solo_game(graph=graph)
    driver = game._evolution_driver
    assert driver is not None
    try:
        # ダミーで spawn 1 体（spawned が空だと finalize_wave が False を返す）
        driver.spawn_enemy((100.0, 100.0))
        assert graph.get_latest() is None
        game._prev_wave_phase = WavePhase.BATTLE
        game._wave_manager._phase = WavePhase.SUMMARY
        game._tick_evolution()
        latest = graph.get_latest()
        assert latest is not None
        # 進化前の世代（1）が記録されている
        assert latest.generation == 1
    finally:
        pg.quit()


def test_solo_game_without_driver_keeps_generation_zero() -> None:
    """EvolutionDriver を渡さない場合は従来通り _generation=0 のまま。"""
    pg.init()
    pg.display.set_mode((400, 200))
    try:
        game = SoloGame(max_wave=1)
        assert game._generation == 0
        # phase 遷移しても進化が動かないこと
        game._prev_wave_phase = WavePhase.BATTLE
        game._wave_manager._phase = WavePhase.SUMMARY
        game._tick_evolution()
        assert game._generation == 0
    finally:
        pg.quit()


def test_evolution_driver_factory_returns_evolved_enemy_with_brain() -> None:
    """EvolutionDriver.spawn_enemy の戻り値が NN を保持した EvolvedEnemy。"""
    manager = EvolutionManager(population_size=3)
    driver = EvolutionDriver(manager=manager)
    enemy = driver.spawn_enemy((50.0, 50.0))
    assert isinstance(enemy, EvolvedEnemy)
    assert enemy.get_brain() is manager.population[0]
    assert enemy.get_generation() == 1


if __name__ == "__main__":
    test_solo_game_uses_driver_as_enemy_factory()
    test_generation_progresses_after_wave_summary()
    test_finalize_wave_appends_to_evolution_graph()
    test_solo_game_without_driver_keeps_generation_zero()
    test_evolution_driver_factory_returns_evolved_enemy_with_brain()
    print("All evolution integration tests passed.")
