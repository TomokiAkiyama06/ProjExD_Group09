"""NumPyで実装する敵移動用の小規模ニューラルネット。"""

from __future__ import annotations

import numpy as np

DEFAULT_INPUT_SIZE: int = 12
DEFAULT_HIDDEN_SIZE: int = 16
DEFAULT_OUTPUT_SIZE: int = 2
WEIGHT_INIT_SCALE: float = 0.5


class NeuralNet:
    """敵1体ごとに保持される小規模ニューラルネット。

    12次元の観測ベクトルを受け取り、移動方向として使う2次元ベクトル
    ``(vx, vy)`` を -1.0 から 1.0 の範囲で返す。
    """

    def __init__(
        self,
        input_size: int = DEFAULT_INPUT_SIZE,
        hidden_size: int = DEFAULT_HIDDEN_SIZE,
        output_size: int = DEFAULT_OUTPUT_SIZE,
    ) -> None:
        """重みとバイアスをランダム初期化する。

        Args:
            input_size: 入力層のノード数
            hidden_size: 隠れ層のノード数
            output_size: 出力層のノード数

        Raises:
            ValueError: いずれかの層サイズが1未満の場合
        """
        self._validate_layer_size("input_size", input_size)
        self._validate_layer_size("hidden_size", hidden_size)
        self._validate_layer_size("output_size", output_size)

        self._input_size: int = input_size
        self._hidden_size: int = hidden_size
        self._output_size: int = output_size
        self._w1: np.ndarray = np.random.randn(input_size, hidden_size) * WEIGHT_INIT_SCALE
        self._b1: np.ndarray = np.zeros(hidden_size)
        self._w2: np.ndarray = np.random.randn(hidden_size, output_size) * WEIGHT_INIT_SCALE
        self._b2: np.ndarray = np.zeros(output_size)

    @property
    def input_size(self) -> int:
        """入力層のノード数を返す。"""
        return self._input_size

    @property
    def hidden_size(self) -> int:
        """隠れ層のノード数を返す。"""
        return self._hidden_size

    @property
    def output_size(self) -> int:
        """出力層のノード数を返す。"""
        return self._output_size

    @property
    def w1(self) -> np.ndarray:
        """入力層から隠れ層への重みを返す。"""
        return self._w1

    @property
    def b1(self) -> np.ndarray:
        """隠れ層のバイアスを返す。"""
        return self._b1

    @property
    def w2(self) -> np.ndarray:
        """隠れ層から出力層への重みを返す。"""
        return self._w2

    @property
    def b2(self) -> np.ndarray:
        """出力層のバイアスを返す。"""
        return self._b2

    def forward(self, input_vec: np.ndarray) -> np.ndarray:
        """順伝播を実行して2次元の移動ベクトルを返す。

        Args:
            input_vec: 入力層に渡す1次元ベクトル

        Returns:
            tanhで -1.0 から 1.0 に収めた出力ベクトル

        Raises:
            ValueError: 入力ベクトルの形が ``(input_size,)`` ではない場合
        """
        x: np.ndarray = np.asarray(input_vec, dtype=float)
        if x.shape != (self._input_size,):
            expected_shape = (self._input_size,)
            raise ValueError(f"input_vec must have shape {expected_shape}, got {x.shape}")

        hidden: np.ndarray = np.tanh(x @ self._w1 + self._b1)
        output: np.ndarray = np.tanh(hidden @ self._w2 + self._b2)
        return output

    def copy(self) -> NeuralNet:
        """同じ重みを持つ独立したニューラルネットを作成する。"""
        clone = NeuralNet(self._input_size, self._hidden_size, self._output_size)
        clone._w1 = self._w1.copy()
        clone._b1 = self._b1.copy()
        clone._w2 = self._w2.copy()
        clone._b2 = self._b2.copy()
        return clone

    @staticmethod
    def _validate_layer_size(name: str, value: int) -> None:
        """層サイズが正の整数であることを検証する。"""
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int, got {type(value).__name__}")
        if value < 1:
            raise ValueError(f"{name} must be greater than 0")
