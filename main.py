"""エントリーポイント。

起動モード（--host / --client --ip=<IP> / --solo）を引数で切り替える。
引数なしの場合は solo モードで起動する。
実体は後続のTaskで埋める。
"""

import argparse
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.solo_game import SoloGame

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _build_solo_kwargs() -> dict:
    """SoloGame / HostGame に注入する combat / towers / presentation / evolution の各コンポーネントをまとめる。"""  # noqa: E501
    from combat import (
        SKILL_CYCLE,
        WEAPON_CYCLE,
        BossEnemy,
        EffectManager,
        WeaponSelectorUI,
        create_special_enemy,
    )
    from core.constants import SOLO_MAX_WAVE
    from evolution import EvolutionDriver, EvolutionManager
    from presentation import EvolutionGraph
    from presentation.sound_manager import SoundManager
    from presentation.tutorial import TutorialOverlay
    from towers import (
        FireTower,
        IceTower,
        LightningTower,
        PhysicalTower,
        TowerSelectorUI,
    )

    evolution_manager = EvolutionManager()
    evolution_graph = EvolutionGraph()
    evolution_driver = EvolutionDriver(
        manager=evolution_manager,
        graph=evolution_graph,
    )
    # SoundManager(auto_load=True) で assets/sound/ 内の SE を自動キャッシュする
    sound = SoundManager()

    return {
        "tower_factories": {
            "fire": FireTower,
            "ice": IceTower,
            "lightning": LightningTower,
            "physical": PhysicalTower,
        },
        "tower_selector": TowerSelectorUI(),
        "effects": EffectManager(),
        "sound": sound,
        "fighter_weapons": [weapon_cls() for weapon_cls in WEAPON_CYCLE],
        "fighter_skills": [skill_cls() for skill_cls in SKILL_CYCLE],
        "weapon_selector": WeaponSelectorUI(),
        # enemy_factory は EvolutionDriver.spawn_enemy が SoloGame 側で自動的に使われる
        "boss_factory": BossEnemy,
        # 特殊敵（fast/shielded）はウェーブ依存の確率で通常枠を置き換えて出現
        "special_factory": create_special_enemy,
        "max_wave": SOLO_MAX_WAVE,
        "evolution_driver": evolution_driver,
        "evolution_graph": evolution_graph,
        "tutorial_overlay": TutorialOverlay(),
    }


def run_host(port: int = 50000) -> None:
    """ホストモード（プレイヤー1、権威サーバ）。

    `core.host_game.HostGame` を起動し、LAN 内の他 PC からの接続を待ち受ける。
    """
    from core.host_game import HostGame

    solo_kwargs = _build_solo_kwargs()
    # LAN 公開のため 0.0.0.0 にバインドし、すべての NIC から受け付ける
    game = HostGame(host="0.0.0.0", port=port, **solo_kwargs)
    game.run()


def run_client(ip: str, port: int = 50000) -> None:
    """クライアントモード（プレイヤー2、描画専用）。

    `core.client_game.ClientGame` を起動してホストに接続する。
    """
    from core.client_game import ClientGame

    game = ClientGame(host=ip, port=port, name="player2")
    game.run()


def run_versus() -> None:
    """対戦モード（同一プロセス内で 2 フィールドを並列駆動）。

    `presentation.VersusGame` を起動する。敵 factory には solo / host と同じ
    `EvolvedEnemy` / `BossEnemy` を渡し、両フィールドで進化対応敵とボスを使う。
    """
    from combat import BossEnemy
    from evolution import EvolvedEnemy
    from presentation.versus_mode import VersusGame

    game = VersusGame(
        enemy_factory=EvolvedEnemy,
        boss_factory=BossEnemy,
        local_side="left",
    )
    game.run()


def create_solo_game() -> "SoloGame":
    """1台2プレイヤーモードに必要な concrete 実装を注入して生成する。"""
    from core.solo_game import SoloGame

    return SoloGame(**_build_solo_kwargs())


def run_solo() -> None:
    """1台2プレイヤーのフォールバックモード。"""
    game = create_solo_game()
    game.run()


def main() -> None:
    """エントリーポイント。argparse で起動モードを切替えて対応する run_* を呼ぶ。"""
    parser = argparse.ArgumentParser(description="共進化の砦（仮）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--host", action="store_true", help="ホストモード（プレイヤー1）")
    group.add_argument("--client", action="store_true", help="クライアントモード（プレイヤー2）")
    group.add_argument("--solo", action="store_true", help="1台2プレイヤーモード")
    group.add_argument("--versus", action="store_true", help="対戦モード（同一PC内 2 フィールド）")
    parser.add_argument("--ip", default="127.0.0.1", help="--client 時の接続先ホストIP")
    parser.add_argument("--port", type=int, default=50000, help="UDP ポート番号")
    args = parser.parse_args()

    if args.host:
        run_host(port=args.port)
    elif args.client:
        run_client(args.ip, port=args.port)
    elif args.versus:
        run_versus()
    else:
        run_solo()


if __name__ == "__main__":
    main()
