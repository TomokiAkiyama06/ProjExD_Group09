"""タワーのアップグレード・売却ロジック。

Lv1〜TOWER_MAX_LEVEL までのアップグレード:
- ダメージ:   `damage * (1 + TOWER_UPGRADE_DAMAGE_BONUS * (level - 1))`
- 射程:       `range * (1 + TOWER_UPGRADE_RANGE_BONUS * (level - 1))`
- クールタイム: `cooldown * (TOWER_UPGRADE_COOLDOWN_MULT ** (level - 1))`

各レベルへの遷移コストは `TOWER_UPGRADE_COST_PER_LEVEL[新Lv-1]`。
売却は累計投資額の `TOWER_SELL_REFUND_RATIO` を返金する。
"""

from __future__ import annotations

from dataclasses import dataclass

from core.base_tower import BaseTower
from core.constants import (
    TOWER_MAX_LEVEL,
    TOWER_SELL_REFUND_RATIO,
    TOWER_UPGRADE_COOLDOWN_MULT,
    TOWER_UPGRADE_COST_PER_LEVEL,
    TOWER_UPGRADE_DAMAGE_BONUS,
    TOWER_UPGRADE_RANGE_BONUS,
)


def get_upgrade_cost(tower: BaseTower) -> int:
    """次のレベルへのアップグレードコスト。最大レベルなら 0。"""
    current = tower.get_level()
    if current >= TOWER_MAX_LEVEL:
        return 0
    next_index = current  # 例: Lv1→2 はインデックス 1
    if next_index < 0 or next_index >= len(TOWER_UPGRADE_COST_PER_LEVEL):
        return 0
    return int(TOWER_UPGRADE_COST_PER_LEVEL[next_index])


def can_upgrade(tower: BaseTower, gold: int) -> bool:
    if tower.get_level() >= TOWER_MAX_LEVEL:
        return False
    return int(gold) >= get_upgrade_cost(tower)


def upgrade(tower: BaseTower, gold: int) -> int:
    """Tower をアップグレードする。

    Args:
        tower: 対象タワー。Lv が最大未満であること。
        gold: 現在の所持リソース。

    Returns:
        アップグレード後の所持リソース。コスト不足や最大Lv の場合は gold をそのまま返す。
    """
    if not can_upgrade(tower, gold):
        return int(gold)
    cost = get_upgrade_cost(tower)
    # ステータス上昇（次の Lv 値を基準に再計算）
    base_damage = tower.get_damage() / _level_damage_mult(tower.get_level())
    base_range = tower.get_range() / _level_range_mult(tower.get_level())
    base_cooldown = tower.get_cooldown() / _level_cooldown_mult(tower.get_level())
    new_level = tower.get_level() + 1
    tower.set_level(new_level)
    tower.set_damage(int(base_damage * _level_damage_mult(new_level)))
    tower.set_range(base_range * _level_range_mult(new_level))
    tower.set_cooldown(base_cooldown * _level_cooldown_mult(new_level))
    tower.add_invested(cost)
    return int(gold) - cost


def sell(tower: BaseTower, gold: int) -> int:
    """Tower を売却して所持リソースに返金分を加算した値を返す。"""
    refund = int(tower.get_total_invested() * TOWER_SELL_REFUND_RATIO)
    return int(gold) + refund


def get_sell_refund(tower: BaseTower) -> int:
    return int(tower.get_total_invested() * TOWER_SELL_REFUND_RATIO)


def _level_damage_mult(level: int) -> float:
    return 1.0 + TOWER_UPGRADE_DAMAGE_BONUS * (level - 1)


def _level_range_mult(level: int) -> float:
    return 1.0 + TOWER_UPGRADE_RANGE_BONUS * (level - 1)


def _level_cooldown_mult(level: int) -> float:
    return TOWER_UPGRADE_COOLDOWN_MULT ** (level - 1)


@dataclass(frozen=True)
class TowerUpgrade:
    """既存呼び出し互換のためのアップグレード差分定義。"""

    name: str
    damage_bonus: int = 0
    range_bonus: float = 0.0
    cooldown_multiplier: float = 1.0

    def apply(self, tower: BaseTower) -> None:
        tower.set_damage(tower.get_damage() + self.damage_bonus)
        tower.set_range(tower.get_range() + self.range_bonus)
        tower.set_cooldown(tower.get_cooldown() * self.cooldown_multiplier)
