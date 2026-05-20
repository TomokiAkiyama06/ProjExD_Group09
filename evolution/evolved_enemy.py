"""NeuralNetで移動方向を決める進化対応敵。"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from core.base_enemy import BaseEnemy
from core.constants import (
    ENEMY_BASE_DAMAGE,
    ENEMY_BASE_HP,
    ENEMY_BASE_REWARD,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

from .neural_net import DEFAULT_INPUT_SIZE, NeuralNet

if TYPE_CHECKING:
    from core.base_tower import BaseTower
    from core.fortress import Fortress


class EvolvedEnemy(BaseEnemy):
    """ニューラルネットで移動方向を判断する敵。"""

    NEARBY_TOWER_LIMIT: int = 3
    TOWER_TYPE_VALUES: ClassVar[dict[str, float]] = {
        "fire": 0.25,
        "ice": 0.5,
        "lightning": 0.75,
        "physical": 1.0,
    }

    def __init__(  # noqa: PLR0913 - BaseEnemy互換の生成引数を受け取るため許容
        self,
        pos: tuple[float, float] = (0.0, 0.0),
        hp: int = ENEMY_BASE_HP,
        brain: NeuralNet | None = None,
        speed: float = BaseEnemy.DEFAULT_SPEED,
        damage: int = ENEMY_BASE_DAMAGE,
        reward: int = ENEMY_BASE_REWARD,
    ) -> None:
        """敵を初期化し、個体ごとのニューラルネットを割り当てる。

        Args:
            pos: 初期位置
            hp: 最大HP兼初期HP
            brain: 移動判断に使うニューラルネット。未指定なら新規生成する
            speed: 移動速度
            damage: 拠点到達時のダメージ
            reward: 撃破時の報酬
        """
        super().__init__(pos=pos, hp=hp, speed=speed, damage=damage, reward=reward)
        self._brain: NeuralNet = brain if brain is not None else NeuralNet()

    @property
    def brain(self) -> NeuralNet:
        """敵が保持するニューラルネットを返す。"""
        return self._brain

    def get_brain(self) -> NeuralNet:
        """敵が保持するニューラルネットを返す。"""
        return self._brain

    def decide(self, inputs: np.ndarray) -> np.ndarray:
        """現在の観測入力から移動方向ベクトルを決定する。"""
        return self.brain.forward(inputs)

    def update(self, fortress: Fortress, dt: float = 1.0 / 60.0) -> None:
        """タワー情報なしでNN移動を行う。"""
        self.update_with_towers(fortress, (), dt)

    def update_with_towers(
        self,
        fortress: Fortress,
        towers: Sequence[BaseTower],
        dt: float = 1.0 / 60.0,
    ) -> None:
        """拠点と近傍タワーを観測し、NNの出力方向へ移動する。

        Args:
            fortress: 目標となる拠点
            towers: 観測対象のタワー一覧
            dt: 経過秒数
        """
        self._update_slow_timer(dt)
        if self._reached or self.is_dead():
            return
        if self._handle_fortress_contact(fortress):
            return

        inputs = self._build_input_vector(fortress, towers)
        velocity = np.asarray(self.decide(inputs), dtype=float)
        vx, vy = self._normalize_output(velocity)
        if vx == 0.0 and vy == 0.0:
            return

        step = self.get_effective_speed() * dt
        x, y = self._pos
        self._pos = (x + vx * step, y + vy * step)
        self._handle_fortress_contact(fortress)

    def _build_input_vector(
        self,
        fortress: Fortress,
        towers: Sequence[BaseTower],
    ) -> np.ndarray:
        """NNへ渡す12次元の観測ベクトルを構築する。"""
        x, y = self._pos
        fx, fy = fortress.get_pos()
        features: list[float] = [
            self._normalize_hp(),
            self._clip((fx - x) / SCREEN_WIDTH),
            self._clip((fy - y) / SCREEN_HEIGHT),
        ]

        sorted_towers = sorted(
            towers,
            key=lambda tower: self._distance_to(tower.get_pos()),
        )
        for tower in sorted_towers[: self.NEARBY_TOWER_LIMIT]:
            tx, ty = tower.get_pos()
            features.extend(
                [
                    self._clip((tx - x) / SCREEN_WIDTH),
                    self._clip((ty - y) / SCREEN_HEIGHT),
                    self._tower_type_value(tower),
                ],
            )

        while len(features) < DEFAULT_INPUT_SIZE:
            features.append(0.0)
        return np.asarray(features[:DEFAULT_INPUT_SIZE], dtype=float)

    def _normalize_hp(self) -> float:
        """現在HPを0.0から1.0に正規化する。"""
        if self._max_hp <= 0:
            return 0.0
        return self._clip(self._hp / self._max_hp, minimum=0.0, maximum=1.0)

    def _distance_to(self, pos: tuple[float, float]) -> float:
        """現在位置から指定座標までの距離を返す。"""
        x, y = self._pos
        px, py = pos
        return math.hypot(px - x, py - y)

    def _tower_type_value(self, tower: BaseTower) -> float:
        """タワー種別をNN入力用のスカラー値へ変換する。"""
        element = getattr(tower, "element", None)
        if isinstance(element, str):
            return self.TOWER_TYPE_VALUES.get(element, 0.1)
        class_name = type(tower).__name__.lower()
        for name, value in self.TOWER_TYPE_VALUES.items():
            if name in class_name:
                return value
        return 0.1

    def _update_slow_timer(self, dt: float) -> None:
        """BaseEnemyと同じslowタイマーを進める。"""
        if self._slow_remaining <= 0.0:
            return
        self._slow_remaining = max(0.0, self._slow_remaining - dt)
        if self._slow_remaining == 0.0:
            self._speed_factor = 1.0

    def _handle_fortress_contact(self, fortress: Fortress) -> bool:
        """拠点接触時にダメージを与え、到達済みにする。"""
        fx, fy = fortress.get_pos()
        x, y = self._pos
        if math.hypot(fx - x, fy - y) > self.CONTACT_DISTANCE:
            return False
        fortress.take_damage(self._damage)
        self._reached = True
        return True

    @staticmethod
    def _normalize_output(output: np.ndarray) -> tuple[float, float]:
        """NN出力を移動方向として扱える範囲に正規化する。"""
        if output.shape != (2,):
            raise ValueError(f"brain output must have shape (2,), got {output.shape}")
        vx = float(output[0])
        vy = float(output[1])
        length = math.hypot(vx, vy)
        if length == 0.0:
            return (0.0, 0.0)
        if length <= 1.0:
            return (vx, vy)
        return (vx / length, vy / length)

    @staticmethod
    def _clip(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
        """値を指定範囲に丸める。"""
        return max(minimum, min(maximum, float(value)))
