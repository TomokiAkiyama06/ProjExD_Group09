"""World state and simple physics helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame as pg

from .base_enemy import BaseEnemy
from .base_player import BasePlayer
from .base_tower import BaseTower
from .bullet import Bullet
from .fortress import Fortress


@dataclass
class World:
    fortress: Fortress = field(default_factory=lambda: Fortress(x=640, y=360))

    players: list[BasePlayer] = field(
        default_factory=lambda: [
            BasePlayer(x=250, y=500, image_name="player_fighter.png"),
            BasePlayer(x=320, y=500, image_name="player_builder.png"),
        ]
    )

    enemies: list[BaseEnemy] = field(
        default_factory=lambda: [
            BaseEnemy(x=120, y=200, image_name="enemy.png"),
            BaseEnemy(x=180, y=200, image_name="enemy_fast.png"),
            BaseEnemy(x=240, y=200, image_name="enemy_shielded.png"),
            BaseEnemy(x=320, y=200, image_name="boss.png", image_size=(64, 64)),
        ]
    )

    towers: list[BaseTower] = field(
        default_factory=lambda: [
            BaseTower(x=430, y=360, image_name="tower_fire.png"),
            BaseTower(x=500, y=360, image_name="tower_ice.png"),
            BaseTower(x=570, y=360, image_name="tower_lightning.png"),
            BaseTower(x=640, y=360, image_name="tower_physical.png"),
        ]
    )

    bullets: list[Bullet] = field(
        default_factory=lambda: [
            Bullet(x=420, y=500),
        ]
    )

    def update(self, dt: float) -> None:
        """ワールド内のオブジェクトを更新する。"""
        for entity in [*self.players, *self.enemies, *self.towers, *self.bullets]:
            update = getattr(entity, "update", None)
            if callable(update):
                update(dt)

        self.bullets = [bullet for bullet in self.bullets if bullet.alive]

    def draw(self, screen: pg.Surface) -> None:
        """ワールド内のオブジェクトを描画する。"""
        for tower in self.towers:
            tower.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for player in self.players:
            player.draw(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        self.fortress.draw(screen)