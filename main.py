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


def run_host() -> None:
    """ホストモード（プレイヤー1、権威サーバ）。"""
    print("not implemented: host mode")


def run_client(ip: str) -> None:
    """クライアントモード（プレイヤー2）。"""
    print(f"not implemented: client mode (host={ip})")


def create_solo_game() -> "SoloGame":
    """1台2プレイヤーモードに必要な concrete 実装を注入して生成する。"""
    from combat import (
        SKILL_CYCLE,
        WEAPON_CYCLE,
        BossEnemy,
        EffectManager,
        WeaponSelectorUI,
    )
    from core.solo_game import SoloGame
    from towers import (
        FireTower,
        IceTower,
        LightningTower,
        PhysicalTower,
        TowerSelectorUI,
    )

    return SoloGame(
        tower_factories={
            "fire": FireTower,
            "ice": IceTower,
            "lightning": LightningTower,
            "physical": PhysicalTower,
        },
        tower_selector=TowerSelectorUI(),
        effects=EffectManager(),
        fighter_weapons=[weapon_cls() for weapon_cls in WEAPON_CYCLE],
        fighter_skills=[skill_cls() for skill_cls in SKILL_CYCLE],
        weapon_selector=WeaponSelectorUI(),
        boss_factory=BossEnemy,
    )


def run_solo() -> None:
    """1台2プレイヤーのフォールバックモード。"""
    game = create_solo_game()
    game.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="共進化の砦（仮）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--host", action="store_true", help="ホストモード（プレイヤー1）")
    group.add_argument("--client", action="store_true", help="クライアントモード（プレイヤー2）")
    group.add_argument("--solo", action="store_true", help="1台2プレイヤーモード")
    parser.add_argument("--ip", default="127.0.0.1", help="--client 時の接続先ホストIP")
    args = parser.parse_args()

    if args.host:
        run_host()
    elif args.client:
        run_client(args.ip)
    else:
        run_solo()


if __name__ == "__main__":
    main()
