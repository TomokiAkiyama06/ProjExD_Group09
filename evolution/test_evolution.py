"""NeuralNetと進化AI補助クラスの単体テスト。

実行方法:
    python -m evolution.test_evolution
"""

from __future__ import annotations

import numpy as np

from evolution.evolution_manager import EvolutionManager
from evolution.neural_net import DEFAULT_INPUT_SIZE, DEFAULT_OUTPUT_SIZE, NeuralNet


def test_forward_shape() -> None:
    """12次元入力で2次元出力が返ることを確認する。"""
    net = NeuralNet()
    output = net.forward(np.zeros(DEFAULT_INPUT_SIZE))
    assert output.shape == (DEFAULT_OUTPUT_SIZE,)


def test_forward_range() -> None:
    """forwardの出力値が -1.0 から 1.0 の範囲に収まることを確認する。"""
    net = NeuralNet()
    output = net.forward(np.ones(DEFAULT_INPUT_SIZE))
    assert np.all((output >= -1.0) & (output <= 1.0))


def test_rejects_wrong_input_shape() -> None:
    """入力次元が違う場合にValueErrorを出すことを確認する。"""
    net = NeuralNet()
    try:
        net.forward(np.zeros(DEFAULT_INPUT_SIZE - 1))
    except ValueError as error:
        assert "input_vec must have shape" in str(error)
    else:
        raise AssertionError("NeuralNet.forward should reject wrong input shape")


def test_weights_roundtrip() -> None:
    """get_weightsからset_weightsへ渡すとforward結果が一致することを確認する。"""
    net = NeuralNet()
    # b1/b2 に非ゼロ値を設定してバイアスのコピー漏れも検出できるようにする
    w1, b1, w2, b2 = net.get_weights()
    b1[:] = np.linspace(-0.5, 0.5, b1.shape[0])
    b2[:] = np.linspace(-0.3, 0.3, b2.shape[0])
    net.set_weights([w1, b1, w2, b2])

    input_vec = np.linspace(0.0, 1.0, DEFAULT_INPUT_SIZE)
    expected = net.forward(input_vec)

    copied_net = NeuralNet()
    weights = net.get_weights()
    copied_net.set_weights(weights)
    assert np.allclose(copied_net.forward(input_vec), expected)

    # set_weights が defensive copy: 渡した配列を変更してもコピー先は影響を受けない
    # w1[0, :] は input_vec[0]==0.0 に対応するため b1 を変更して確実に検出する
    weights[1][0] += 999.0
    assert np.allclose(copied_net.forward(input_vec), expected)

    # get_weights が defensive copy: 返された配列を変更しても元のNNは影響を受けない
    leaked = net.get_weights()
    leaked[1][0] += 999.0
    assert np.allclose(net.forward(input_vec), expected)


def test_clone_independence() -> None:
    """clone後に元の重みを変更してもコピーへ影響しないことを確認する。"""
    net = NeuralNet()
    cloned_net = net.clone()
    original_weights = cloned_net.get_weights()

    # set_weightsによる配列差し替えでなくin-place変更で浅いコピーバグも検出する
    net.w1[0, 0] += 1.0
    net.b1[0] += 1.0
    net.w2[0, 0] += 1.0
    net.b2[0] += 1.0

    assert np.array_equal(cloned_net.w1, original_weights[0])
    assert np.array_equal(cloned_net.b1, original_weights[1])
    assert np.array_equal(cloned_net.w2, original_weights[2])
    assert np.array_equal(cloned_net.b2, original_weights[3])


def test_neural_net_forward_shape() -> None:
    """既存CI互換のためforward shapeテストを実行する。"""
    test_forward_shape()


def test_neural_net_forward_output_range() -> None:
    """既存CI互換のためforward rangeテストを実行する。"""
    test_forward_range()


def test_neural_net_rejects_wrong_input_shape() -> None:
    """既存CI互換のため入力形状テストを実行する。"""
    test_rejects_wrong_input_shape()


def test_neural_net_set_weights_matches_forward_result() -> None:
    """既存CI互換のため重みroundtripテストを実行する。"""
    test_weights_roundtrip()


def test_neural_net_clone_keeps_independent_weights() -> None:
    """既存CI互換のためclone独立性テストを実行する。"""
    test_clone_independence()


def test_evolution_manager_uses_default_neural_net_shape() -> None:
    """EvolutionManagerがNeuralNet標準サイズを使うことを確認する。"""
    manager = EvolutionManager(population_size=2)
    assert manager.population[0].input_size == DEFAULT_INPUT_SIZE
    assert manager.population[0].output_size == DEFAULT_OUTPUT_SIZE


def test_next_generation_keeps_population_size() -> None:
    """次世代生成後も個体数が変わらないことを確認する。"""
    manager = EvolutionManager(population_size=6)
    generation = manager.next_generation([1, 2, 3, 4, 5, 6])
    assert len(generation) == 6


def _run_test(name: str, test_func: object) -> None:
    """テスト関数を実行し、成功した項目名を表示する。"""
    if not callable(test_func):
        raise TypeError(f"{name} is not callable")
    test_func()
    print(f"[OK] {name}")


if __name__ == "__main__":
    for test_name, function in (
        ("test_forward_shape", test_forward_shape),
        ("test_forward_range", test_forward_range),
        ("test_weights_roundtrip", test_weights_roundtrip),
        ("test_clone_independence", test_clone_independence),
        ("test_rejects_wrong_input_shape", test_rejects_wrong_input_shape),
        (
            "test_evolution_manager_uses_default_neural_net_shape",
            test_evolution_manager_uses_default_neural_net_shape,
        ),
        ("test_next_generation_keeps_population_size", test_next_generation_keeps_population_size),
    ):
        _run_test(test_name, function)
    print("All tests passed.")
