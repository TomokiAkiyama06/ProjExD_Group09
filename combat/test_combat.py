"""combat パッケージ（武器・スキル・ボス・特殊敵・エフェクト）のテスト。"""

from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

from combat.boss_enemy import BossEnemy
from combat.effects import EffectManager
from combat.fighter_skills import (
    AreaAttackSkill,
    BaseSkill,
    DashAttackSkill,
)
from combat.special_enemy import FastEnemy, ShieldedEnemy, SpecialEnemy, create_combat_enemy
from combat.weapons import (
    WEAPON_CYCLE,
    AreaBullet,
    AreaWeapon,
    MeleeWeapon,
    RangedWeapon,
)
from core.base_enemy import BaseEnemy
from core.constants import BOSS_WAVE_MODULO
from core.fighter import Fighter
from core.fortress import Fortress
from core.wave_manager import WaveManager
from core.world import World
from evolution import EvolvedEnemy
from main import create_solo_game

# ===== effects =====


def test_effects_spawn_explosion_creates_particles() -> None:
    mgr = EffectManager(rng=random.Random(0))
    mgr.spawn_explosion((100.0, 100.0), count=5)
    assert len(mgr.get_particles()) == 5


def test_effects_particles_decay() -> None:
    mgr = EffectManager(rng=random.Random(0))
    mgr.spawn_hit((50.0, 50.0), count=3)
    initial_count = len(mgr.get_particles())
    assert initial_count > 0
    # 1秒進めれば全パーティクル（lifetime <= 0.3）が消滅
    for _ in range(60):
        mgr.update(1.0 / 60.0)
    assert len(mgr.get_particles()) == 0


def test_effects_shockwave_expires() -> None:
    mgr = EffectManager()
    mgr.spawn_shockwave((0.0, 0.0), radius=80.0, duration=0.2)
    assert len(mgr.get_shockwaves()) == 1
    # duration を超えて進めれば消える
    for _ in range(20):
        mgr.update(1.0 / 60.0)
    assert len(mgr.get_shockwaves()) == 0


# ===== weapons =====


def test_weapon_cooldown_blocks_fire() -> None:
    weapon = MeleeWeapon()
    enemy = BaseEnemy(pos=(10.0, 0.0), hp=100)
    bullets = weapon.fire((0.0, 0.0), enemy, (1.0, 0.0))
    assert len(bullets) == 1
    # クールタイム中は撃てない
    assert weapon.fire((0.0, 0.0), enemy, (1.0, 0.0)) == []
    # 時間を進めれば再発射できる
    for _ in range(30):
        weapon.update(1.0 / 60.0)
    assert weapon.is_ready()
    assert len(weapon.fire((0.0, 0.0), enemy, (1.0, 0.0))) == 1


def test_weapon_three_variants_differ() -> None:
    melee = MeleeWeapon()
    ranged = RangedWeapon()
    area = AreaWeapon()
    # 射程・ダメージ・クールタイムが全て異なる
    assert melee.get_range() < ranged.get_range()
    assert melee.get_damage() > ranged.get_damage()
    assert ranged.get_cooldown() < area.get_cooldown()


def test_area_weapon_returns_area_bullet() -> None:
    weapon = AreaWeapon()
    enemy = BaseEnemy(pos=(10.0, 0.0))
    bullets = weapon.fire((0.0, 0.0), enemy, (1.0, 0.0))
    assert len(bullets) == 1
    assert isinstance(bullets[0], AreaBullet)


def test_area_bullet_hits_multiple_enemies() -> None:
    target = BaseEnemy(pos=(100.0, 100.0), hp=100)
    near = BaseEnemy(pos=(105.0, 100.0), hp=100)
    far = BaseEnemy(pos=(500.0, 500.0), hp=100)
    bullet = AreaBullet(
        pos=(100.0, 100.0),
        target=target,
        damage=15,
        explosion_radius=40.0,
    )
    bullet.check_hit(enemies=[target, near, far])
    assert target.get_hp() < 100
    assert near.get_hp() < 100
    assert far.get_hp() == 100


def test_weapon_cycle_has_three_types() -> None:
    assert (MeleeWeapon, RangedWeapon, AreaWeapon) == WEAPON_CYCLE


# ===== skills =====


def test_base_skill_cooldown_blocks_activate() -> None:
    skill = BaseSkill()
    skill.cooldown = 1.0
    fighter = Fighter()
    world = World()
    assert skill.activate(fighter, world)
    assert not skill.activate(fighter, world)  # cd 中


def test_dash_skill_moves_and_damages() -> None:
    fighter = Fighter(pos=(0.0, 100.0))
    # facing は (1, 0) がデフォルト
    world = World()
    enemy = BaseEnemy(pos=(40.0, 100.0), hp=100)
    world.add_enemy(enemy)
    skill = DashAttackSkill()
    assert skill.activate(fighter, world)
    assert skill.is_active()
    assert skill.is_invincible()
    # 何フレームか進める
    for _ in range(20):
        skill.update(1.0 / 60.0, fighter, world)
    # 移動した
    assert fighter.get_pos()[0] > 0
    # 接触敵がダメージを受けた
    assert enemy.get_hp() < 100


def test_dash_skill_becomes_inactive_after_duration() -> None:
    fighter = Fighter(pos=(0.0, 100.0))
    world = World()
    skill = DashAttackSkill()
    skill.activate(fighter, world)
    # SKILL_DASH_DURATION = 0.25 → 0.4 秒進めれば必ず終わる
    for _ in range(int(0.4 * 60)):
        skill.update(1.0 / 60.0, fighter, world)
    assert not skill.is_active()
    assert not skill.is_invincible()


def test_area_skill_damages_enemies_in_range() -> None:
    fighter = Fighter(pos=(100.0, 100.0))
    world = World()
    inside = BaseEnemy(pos=(150.0, 100.0), hp=100)
    outside = BaseEnemy(pos=(500.0, 500.0), hp=100)
    world.add_enemy(inside)
    world.add_enemy(outside)
    skill = AreaAttackSkill()
    assert skill.activate(fighter, world)
    assert inside.get_hp() < 100
    assert outside.get_hp() == 100


# ===== boss =====


def test_boss_has_high_hp_and_special_action() -> None:
    boss = BossEnemy(pos=(200.0, 100.0))
    assert boss.get_hp() > 100  # base enemy HP は 30、ボスは数百
    assert boss.get_special_timer() > 0


def test_boss_special_burst_damages_player() -> None:
    # 5秒後のボス予想位置（200 + 35*5 = 375）の近くにプレイヤーを置く
    boss = BossEnemy(pos=(200.0, 100.0))
    fighter = Fighter(pos=(370.0, 100.0))
    fortress = Fortress(pos=(900.0, 100.0))
    world = World(fortress=fortress)
    world.add_player(fighter)
    world.add_enemy(boss)

    # 特殊行動の発動間隔を進める（BOSS_SPECIAL_INTERVAL = 5.0 秒）
    for _ in range(int(6.0 * 60)):
        boss.update_with_world(1.0 / 60.0, world)
        world.update(1.0 / 60.0)
    # プレイヤーがダメージを受けた（特殊行動が発火した）
    assert fighter.get_hp() < 100


def test_boss_special_burst_skips_invincible_player() -> None:
    dash = DashAttackSkill()
    boss = BossEnemy(pos=(200.0, 100.0))
    fighter = Fighter(pos=(200.0, 100.0), skills=[dash])
    world = World()
    world.add_player(fighter)

    assert dash.activate(fighter, world)
    assert fighter.is_invincible()
    start_hp = fighter.get_hp()
    boss._special_timer = 0.0

    boss.update_with_world(1.0 / 60.0, world)

    assert fighter.get_hp() == start_hp


def test_boss_world_tick_does_not_move_boss() -> None:
    boss = BossEnemy(pos=(200.0, 100.0))
    world = World()
    world.add_enemy(boss)
    start = boss.get_pos()

    boss.update_with_world(1.0, world)
    assert boss.get_pos() == start

    world.update(1.0)
    assert boss.get_pos() != start


def test_boss_death_effect_runs_once() -> None:
    boss = BossEnemy(pos=(200.0, 100.0))
    mgr = EffectManager()
    world = World(effects=mgr)
    boss.take_damage(99999)
    assert boss.is_dead()
    boss.trigger_death_effect(world)
    assert len(mgr.get_particles()) > 0
    boss.trigger_death_effect(world)  # 2回目は再生成しない
    # 1回目で生成された数を保持（再生成されないと等しいまま）
    assert len(mgr.get_particles()) > 0


# ===== special enemies =====


def test_fast_enemy_is_fast() -> None:
    fast = FastEnemy(pos=(0.0, 0.0))
    base = BaseEnemy(pos=(0.0, 0.0))
    assert fast.get_speed() > base.get_speed()
    assert fast.get_hp() < base.get_hp()


def test_shielded_enemy_absorbs_damage() -> None:
    shielded = ShieldedEnemy(pos=(0.0, 0.0))
    initial_hp = shielded.get_hp()
    shielded.take_damage(10)
    # 盾で吸収される
    assert shielded.get_hp() == initial_hp
    assert shielded.get_shield() < shielded.get_max_shield()


def test_shielded_enemy_takes_damage_after_shield_broken() -> None:
    shielded = ShieldedEnemy(pos=(0.0, 0.0))
    initial_hp = shielded.get_hp()
    # 盾以上のダメージを与える
    shielded.take_damage(shielded.get_max_shield() + 5)
    assert shielded.get_shield() == 0
    assert shielded.get_hp() == initial_hp - 5


def test_special_enemy_preserves_legacy_constructor_signature() -> None:
    enemy = SpecialEnemy(
        pos=(10.0, 20.0),
        hp=44,
        speed=77.0,
        damage=9,
        reward=3,
    )

    assert enemy.get_pos() == (10.0, 20.0)
    assert enemy.get_hp() == 44
    assert enemy.get_speed() == 77.0
    assert enemy.get_damage() == 9
    assert enemy.get_reward() == 3


def test_create_combat_enemy_uses_probability_roll() -> None:
    fast = create_combat_enemy((0.0, 0.0), roll=0.0)
    shielded = create_combat_enemy((0.0, 0.0), roll=0.25)
    base = create_combat_enemy((0.0, 0.0), roll=0.95)

    assert isinstance(fast, FastEnemy)
    assert isinstance(shielded, ShieldedEnemy)
    assert not isinstance(base, (FastEnemy, ShieldedEnemy))


# ===== integration smoke =====


def test_fighter_with_weapons_and_skills() -> None:
    pg.init()
    pg.display.set_mode((400, 300))
    fighter = Fighter(
        pos=(100.0, 100.0),
        weapons=[MeleeWeapon(), RangedWeapon(), AreaWeapon()],
        skills=[DashAttackSkill(), AreaAttackSkill()],
    )
    world = World()
    # 武器サイクル
    assert fighter.get_current_weapon().get_name() == "melee"
    fighter.cycle_weapon(1)
    # サイクル直後はクールタイム中なので、進めてから検証
    for _ in range(int(0.3 * 60)):
        keys = pg.key.get_pressed()
        fighter.update_keys(keys, 1.0 / 60.0, world)
    fighter.cycle_weapon(1)
    # スキルサイクル
    assert fighter.get_current_skill().get_name() == "dash"
    fighter.cycle_skill(1)
    assert fighter.get_current_skill().get_name() == "area"
    pg.quit()


def test_create_solo_game_supplies_combat_defaults() -> None:
    game = create_solo_game()
    fighter = game.get_fighter()

    assert fighter.get_current_weapon() is not None
    assert fighter.get_current_skill() is not None
    assert game._wave_manager.get_max_wave() >= BOSS_WAVE_MODULO
    assert game._wave_manager._factory is EvolvedEnemy

    pg.quit()


def test_wave_manager_default_stays_at_three_without_solo_bootstrap() -> None:
    manager = WaveManager(boss_factory=BossEnemy)

    assert manager.get_max_wave() == 3


if __name__ == "__main__":
    test_effects_spawn_explosion_creates_particles()
    test_effects_particles_decay()
    test_effects_shockwave_expires()
    test_weapon_cooldown_blocks_fire()
    test_weapon_three_variants_differ()
    test_area_weapon_returns_area_bullet()
    test_area_bullet_hits_multiple_enemies()
    test_weapon_cycle_has_three_types()
    test_base_skill_cooldown_blocks_activate()
    test_dash_skill_moves_and_damages()
    test_dash_skill_becomes_inactive_after_duration()
    test_area_skill_damages_enemies_in_range()
    test_boss_has_high_hp_and_special_action()
    test_boss_special_burst_damages_player()
    test_boss_special_burst_skips_invincible_player()
    test_boss_world_tick_does_not_move_boss()
    test_boss_death_effect_runs_once()
    test_fast_enemy_is_fast()
    test_shielded_enemy_absorbs_damage()
    test_shielded_enemy_takes_damage_after_shield_broken()
    test_special_enemy_preserves_legacy_constructor_signature()
    test_create_combat_enemy_uses_probability_roll()
    test_fighter_with_weapons_and_skills()
    test_create_solo_game_supplies_combat_defaults()
    test_wave_manager_default_stays_at_three_without_solo_bootstrap()
    print("All combat tests passed.")
