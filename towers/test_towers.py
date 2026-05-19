"""towers パッケージ（4属性 + アップグレード + 選択UI）のテスト。"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

from core.base_enemy import BaseEnemy
from core.builder import Builder
from core.fortress import Fortress
from core.world import World
from towers.fire_tower import FireBullet, FireTower
from towers.ice_tower import IceBullet
from towers.lightning_tower import LightningBolt, LightningTower
from towers.physical_tower import PhysicalTower
from towers.tower_selector_ui import TowerSelectorUI
from towers.tower_upgrade import (
    TowerUpgrade,
    can_upgrade,
    get_sell_refund,
    get_upgrade_cost,
    sell,
    upgrade,
)

# ===== fire =====


def test_fire_tower_aoe_hits_multiple() -> None:
    target = BaseEnemy(pos=(100.0, 100.0), hp=100)
    near = BaseEnemy(pos=(110.0, 105.0), hp=100)
    far = BaseEnemy(pos=(300.0, 300.0), hp=100)
    bullet = FireBullet(pos=(100.0, 100.0), target=target, damage=20, explosion_radius=50.0)
    hit = bullet.check_hit(enemies=[target, near, far])
    assert hit
    assert target.get_hp() < 100
    assert near.get_hp() < 100
    assert far.get_hp() == 100  # 範囲外


def test_fire_tower_attack_returns_fire_bullet() -> None:
    tower = FireTower(pos=(0.0, 0.0))
    enemy = BaseEnemy(pos=(50.0, 0.0))
    bullet = tower.attack(enemy)
    assert isinstance(bullet, FireBullet)


# ===== ice =====


def test_ice_bullet_applies_slow() -> None:
    enemy = BaseEnemy(pos=(0.0, 0.0))
    assert enemy.get_speed_factor() == 1.0
    bullet = IceBullet(
        pos=(0.0, 0.0),
        target=enemy,
        damage=1,
        slow_factor=0.5,
        slow_duration=2.0,
    )
    assert bullet.check_hit()
    assert enemy.get_speed_factor() == 0.5
    assert enemy.get_slow_remaining() == 2.0


def test_ice_slow_decays_over_time() -> None:
    enemy = BaseEnemy(pos=(0.0, 0.0))
    fortress = Fortress(pos=(1000.0, 0.0))
    enemy.apply_slow(0.5, 1.0)
    # 1秒経過 → factor 戻る
    for _ in range(60):
        enemy.update(fortress, dt=1.0 / 60.0)
    assert enemy.get_speed_factor() == 1.0


# ===== lightning =====


def test_lightning_tower_chains_to_multiple_enemies() -> None:
    tower = LightningTower(pos=(0.0, 0.0))
    enemies = [
        BaseEnemy(pos=(40.0, 0.0), hp=100),  # 一番近い
        BaseEnemy(pos=(80.0, 0.0), hp=100),  # 連鎖先
        BaseEnemy(pos=(120.0, 0.0), hp=100),  # さらに連鎖
        BaseEnemy(pos=(500.0, 500.0), hp=100),  # 範囲外
    ]
    bullets = tower.update(enemies, now=10.0)
    assert len(bullets) == 1
    assert isinstance(bullets[0], LightningBolt)
    assert enemies[0].get_hp() < 100
    assert enemies[1].get_hp() < 100
    assert enemies[2].get_hp() < 100
    assert enemies[3].get_hp() == 100


def test_lightning_bolt_no_damage_on_check_hit() -> None:
    enemy = BaseEnemy(pos=(0.0, 0.0), hp=50)
    bolt = LightningBolt(chain_points=[(0.0, 0.0), (10.0, 0.0)])
    assert bolt.check_hit(enemies=[enemy]) is False
    assert enemy.get_hp() == 50  # 既に update 時点で適用済みのため


def test_lightning_bolt_expires_after_duration() -> None:
    bolt = LightningBolt(chain_points=[(0, 0), (10, 0)], duration=0.1)
    assert not bolt.is_consumed()
    bolt.update(dt=0.2)
    assert bolt.is_consumed()


# ===== physical =====


def test_physical_tower_high_damage() -> None:
    tower = PhysicalTower(pos=(0.0, 0.0))
    enemy = BaseEnemy(pos=(50.0, 0.0), hp=100)
    bullet = tower.attack(enemy)
    assert bullet is not None
    # 高HP（残100%）→ pierce ボーナスがフルにかかる
    assert bullet.get_damage() > tower.get_damage()


def test_physical_pierce_falls_with_hp() -> None:
    tower = PhysicalTower(pos=(0.0, 0.0))
    full_hp_enemy = BaseEnemy(pos=(50.0, 0.0), hp=100)
    low_hp_enemy = BaseEnemy(pos=(50.0, 0.0), hp=100)
    low_hp_enemy.take_damage(80)  # 残20HP
    full_bullet = tower.attack(full_hp_enemy)
    low_bullet = tower.attack(low_hp_enemy)
    assert full_bullet is not None
    assert low_bullet is not None
    assert full_bullet.get_damage() > low_bullet.get_damage()


# ===== upgrade =====


def test_upgrade_increases_damage_range_and_reduces_cooldown() -> None:
    tower = FireTower(pos=(0.0, 0.0), purchase_cost=30)
    base_damage = tower.get_damage()
    base_range = tower.get_range()
    base_cooldown = tower.get_cooldown()

    gold = 100
    assert can_upgrade(tower, gold)
    cost = get_upgrade_cost(tower)
    new_gold = upgrade(tower, gold)

    assert tower.get_level() == 2
    assert new_gold == gold - cost
    assert tower.get_damage() > base_damage
    assert tower.get_range() > base_range
    assert tower.get_cooldown() < base_cooldown
    assert tower.get_total_invested() == 30 + cost


def test_upgrade_stops_at_max_level() -> None:
    tower = FireTower(pos=(0.0, 0.0), purchase_cost=30)
    gold = 1000
    # Lv1 → Lv2 → Lv3 までは上がる
    gold = upgrade(tower, gold)
    gold = upgrade(tower, gold)
    assert tower.get_level() == 3
    # それ以上は上がらない
    assert not can_upgrade(tower, gold)
    same_gold = upgrade(tower, gold)
    assert same_gold == gold
    assert tower.get_level() == 3


def test_upgrade_fails_when_gold_insufficient() -> None:
    tower = FireTower(pos=(0.0, 0.0), purchase_cost=30)
    new_gold = upgrade(tower, gold=5)
    assert tower.get_level() == 1
    assert new_gold == 5


def test_sell_returns_half_invested() -> None:
    tower = FireTower(pos=(0.0, 0.0), purchase_cost=40)
    upgrade(tower, gold=100)  # Lv2、累計 40 + 30 = 70
    refund = get_sell_refund(tower)
    assert refund == int(70 * 0.5)
    new_gold = sell(tower, gold=10)
    assert new_gold == 10 + refund


def test_tower_upgrade_dataclass_apply() -> None:
    tower = FireTower(pos=(0.0, 0.0))
    base_damage = tower.get_damage()
    up = TowerUpgrade(name="boost", damage_bonus=5, range_bonus=10.0)
    up.apply(tower)
    assert tower.get_damage() == base_damage + 5


# ===== selector UI smoke test =====


def test_tower_selector_ui_draws_without_crash() -> None:
    pg.init()
    pg.display.set_mode((400, 300))
    surface = pg.Surface((400, 300))
    builder = Builder(
        pos=(50.0, 50.0),
        tower_factories={"fire": FireTower},
    )
    world = World()
    ui = TowerSelectorUI()
    ui.draw(surface, builder=builder, world=world, mouse_pos=(200, 150))
    pg.quit()


if __name__ == "__main__":
    test_fire_tower_aoe_hits_multiple()
    test_fire_tower_attack_returns_fire_bullet()
    test_ice_bullet_applies_slow()
    test_ice_slow_decays_over_time()
    test_lightning_tower_chains_to_multiple_enemies()
    test_lightning_bolt_no_damage_on_check_hit()
    test_lightning_bolt_expires_after_duration()
    test_physical_tower_high_damage()
    test_physical_pierce_falls_with_hp()
    test_upgrade_increases_damage_range_and_reduces_cooldown()
    test_upgrade_stops_at_max_level()
    test_upgrade_fails_when_gold_insufficient()
    test_sell_returns_half_invested()
    test_tower_upgrade_dataclass_apply()
    test_tower_selector_ui_draws_without_crash()
    print("All tower tests passed.")
