"""SoloGame に進化AIが組み込まれていることの統合テスト。"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

from core.solo_game import SoloGame
from core.wave_manager import WaveManager
from evolution.evolution_driver import EvolutionDriver
from evolution.evolution_manager import EvolutionManager
from evolution.evolved_enemy import EvolvedEnemy
from presentation.evolution_graph import EvolutionGraph

DRIVE_DT: float = 1.0 / 20.0


def _make_solo_game(
    graph: EvolutionGraph | None = None,
    population_size: int = 4,
) -> tuple[SoloGame, EvolutionDriver]:
    """Driver/Graph 注入済みの SoloGame と driver を作る共通ヘルパ。"""
    pg.init()
    pg.display.set_mode((400, 200))
    manager = EvolutionManager(population_size=population_size)
    driver = EvolutionDriver(manager=manager, graph=graph)
    game = SoloGame(
        evolution_driver=driver,
        evolution_graph=graph,
        max_wave=2,
    )
    return game, driver


def _drive_until_enemy_spawned(game: SoloGame) -> list[EvolvedEnemy]:
    """通常の update だけで最初の敵が spawn するまで進める。"""
    max_seconds = WaveManager.PREPARE_SECONDS + WaveManager.SPAWN_INTERVAL + 1.0
    for _ in range(int(max_seconds / DRIVE_DT)):
        game.update(DRIVE_DT)
        enemies = game.get_world().get_enemies()
        if enemies:
            assert all(isinstance(enemy, EvolvedEnemy) for enemy in enemies)
            return [enemy for enemy in enemies if isinstance(enemy, EvolvedEnemy)]
    raise AssertionError("敵がスポーンしない")


def _defeat_visible_enemies(game: SoloGame) -> None:
    """現在 World にいる敵を倒し、ウェーブ進行を速める。"""
    for enemy in list(game.get_world().get_enemies()):
        enemy.take_damage(enemy.get_hp())


def _drive_until_generation(
    game: SoloGame,
    driver: EvolutionDriver,
    target_generation: int,
) -> None:
    """通常の update を進め、指定世代に到達するまで敵を順次倒す。"""
    max_seconds = (
        WaveManager.PREPARE_SECONDS
        + WaveManager.SPAWN_INTERVAL * (WaveManager.BASE_SPAWN_COUNT + 1)
        + WaveManager.SUMMARY_SECONDS
        + 2.0
    )
    for _ in range(int(max_seconds / DRIVE_DT)):
        game.update(DRIVE_DT)
        _defeat_visible_enemies(game)
        if driver.get_generation() >= target_generation:
            return
    raise AssertionError(f"世代が {target_generation} まで進まない")


def test_solo_game_uses_driver_as_enemy_factory() -> None:
    """SoloGame が EvolutionDriver.spawn_enemy を enemy_factory として使う。"""
    game, _driver = _make_solo_game()
    try:
        enemies = _drive_until_enemy_spawned(game)
        assert enemies
        assert all(enemy.get_generation() == 1 for enemy in enemies)
    finally:
        pg.quit()


def test_generation_progresses_after_wave_summary() -> None:
    """BATTLE → SUMMARY 遷移で世代が進み SoloGame の表示世代も更新される。"""
    game, driver = _make_solo_game()
    try:
        assert driver.get_generation() == 1
        assert game.get_generation() == 1

        _drive_until_generation(game, driver, target_generation=2)

        assert driver.get_generation() == 2
        assert game.get_generation() == 2
    finally:
        pg.quit()


def test_finalize_wave_appends_to_evolution_graph() -> None:
    """ウェーブ完了時に EvolutionGraph.add が呼ばれて履歴が増える。"""
    graph = EvolutionGraph()
    game, driver = _make_solo_game(graph=graph)
    try:
        assert graph.get_latest() is None

        _drive_until_generation(game, driver, target_generation=2)

        latest = graph.get_latest()
        assert latest is not None
        assert latest.generation == 1
    finally:
        pg.quit()


def test_solo_game_without_driver_keeps_generation_zero() -> None:
    """EvolutionDriver を渡さない場合は従来通り generation=0 のまま。"""
    pg.init()
    pg.display.set_mode((400, 200))
    try:
        game = SoloGame(max_wave=1)
        assert game.get_generation() == 0

        for _ in range(int((WaveManager.PREPARE_SECONDS + 1.0) / DRIVE_DT)):
            game.update(DRIVE_DT)

        assert game.get_generation() == 0
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
