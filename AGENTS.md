# AGENTS.md

このファイルは、AIコーディングアシスタント（Claude Code, Cursor, GitHub Copilot, ChatGPT等）がこのリポジトリで作業する際に従うべきルールをまとめたものです。人間の開発メンバーも一読してください。

> **本プロジェクトについて**：東京工科大学 プロジェクト演習D の共同開発課題。pygame製の2人協力プレイ・タワーディフェンスゲームを5人グループで開発します。詳細は `README.md` と `docs/DESIGN.md` を参照。

---

## 1. このリポジトリで何をしているか

* **プロジェクト**：共進化の砦（仮）— LAN対応の2人協力タワーディフェンス
* **言語/環境**：Python 3.10+, pygame 2.1+, NumPy 1.24+
* **特徴**：敵が遺伝的ニューラルネットで進化する／UDPによるLAN通信
* **チーム構成**：5人（基本機能担当2人＋追加機能担当5人、一部兼任）
* **提出形式**：機能ブランチごとに個人実装 → 第6回でマージ

---

## 2. AIアシスタントが守るべき基本ルール

### 2.1 必ず守ること

1. **`main.py` の冒頭には必ず以下を記述する**（授業の必須要件）：
   ```python
   import os
   os.chdir(os.path.dirname(os.path.abspath(__file__)))
   ```
2. **既存のディレクトリ構造を勝手に変更しない**。新規ファイルは適切なサブパッケージ内に追加する
3. **担当領域外のファイルを編集しない**。`core/` 以下の変更は基本機能担当者のみ
4. **コード規約（後述）に従う**：命名規則、docstring、型ヒント
5. **`pygame`以外の重い外部ライブラリは追加しない**（NumPy はOK）
6. **生成AIによる完全な丸パクりコードを出力しない**：参考にしつつ、このプロジェクト固有の構造に合わせて再構成する（授業の評価基準）

### 2.2 やってはいけないこと

* `import os; os.chdir(...)` を `main.py` 以外で実行する
* グローバル変数を多用する（クラス設計を崩す）
* `from xxx import *` を使う
* マジックナンバーをコード中に直接書く（`constants.py` を使う）
* PyTorch / TensorFlow を導入する（NumPyのみで進化AIを実装する方針）
* `print()` でデバッグログを残したままコミットする（最低限、コメントアウトする）

---

## 3. ディレクトリ構造とパッケージ責任

```
ex5/
├─ main.py                  # エントリーポイント（代表者管理）
├─ README.md                # 各自が「分担追加機能」セクションを追記
├─ AGENTS.md                # このファイル
├─ requirements.txt
├─ .gitignore
│
├─ core/                    # ★ベース・基本機能担当2人★
├─ evolution/               # ★担当①：進化AI★
├─ network/                 # ★担当②：通信★
├─ towers/                  # ★担当③：タワー属性★
├─ combat/                  # ★担当④：戦闘・演出★
├─ presentation/            # ★担当⑤：対戦・可視化★
├─ assets/                  # 素材（全員が読み取り、追加は要相談）
└─ docs/                    # ドキュメント
```

### 3.1 各パッケージの役割

| パッケージ | 役割 | 触ってよい担当者 |
|-----------|------|------------------|
| `core/` | 全員が依存する基盤クラスと共通定数 | 基本機能担当2人のみ（他は要相談） |
| `evolution/` | 遺伝的ニューラルネットによる敵進化 | 担当①のみ |
| `network/` | UDP通信、メッセージプロトコル | 担当②のみ |
| `towers/` | タワー属性ごとの派生クラス | 担当③のみ |
| `combat/` | 武器・スキル・ボス・エフェクト | 担当④のみ |
| `presentation/` | 対戦モード、グラフ、サウンド | 担当⑤のみ |
| `assets/` | 画像・音・フォント | 全員が読み取り可、追加は要相談 |
| `docs/` | 設計書・READMEで使う画像 | 代表者管理 |

### 3.2 パッケージ間の依存関係

* すべてのパッケージは `core/` に依存してよい
* `evolution/` と `network/` は**互いに依存しない**（疎結合）
* `towers/`, `combat/` は `core/` にのみ依存
* `presentation/` は `evolution/` `network/` `core/` に依存してよい
* **循環依存を作らないこと**

### 3.3 importの書き方

```python
# 良い例：絶対インポートを使う
from core.base_enemy import BaseEnemy
from core.constants import SCREEN_WIDTH

# 悪い例：相対インポートで階層を遡る
from ..core.base_enemy import BaseEnemy  # 避ける

# 悪い例：ワイルドカードインポート
from core.constants import *  # 禁止
```

---

## 4. コード規約

### 4.1 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| クラス名 | `PascalCase` | `FireTower`, `EvolutionManager` |
| 関数・メソッド | `snake_case` | `update_position`, `calc_fitness` |
| インスタンス変数 | `_snake_case`（先頭アンダースコア） | `self._hp`, `self._neural_net` |
| ローカル変数 | `snake_case` | `enemy_count`, `damage` |
| 定数 | `UPPER_SNAKE_CASE` | `SCREEN_WIDTH`, `NET_PORT` |
| ファイル名 | `snake_case.py` | `fire_tower.py`, `neural_net.py` |
| プライベートメソッド | `_snake_case` | `def _calculate_internal(self):` |

### 4.2 型ヒント

* すべての関数・メソッドの引数と戻り値に型ヒントを付ける
* インスタンス変数にも可能な限り付ける

```python
# 良い例
def attack(self, target: "BaseEnemy", damage: int = 10) -> bool:
    """攻撃を行う。"""
    ...

# 悪い例
def attack(self, target, damage=10):
    ...
```

### 4.3 docstring

* すべての関数・メソッド・クラスにdocstringを書く
* Googleスタイル または シンプルな日本語の説明文を使う
* 引数・戻り値・例外の記述を推奨

```python
def evolve_population(self, fitness_scores: list[float]) -> None:
    """次世代の個体群を生成する。

    エリート選択・トーナメント選択・一様交叉・突然変異を用いて、
    次世代のNN個体群を `self._population` に格納する。

    Args:
        fitness_scores: 現世代の各個体の適応度のリスト
    """
    ...
```

### 4.4 マジックナンバー禁止

```python
# 悪い例
if enemy.x > 1280:
    ...

# 良い例
from core.constants import SCREEN_WIDTH
if enemy.x > SCREEN_WIDTH:
    ...
```

### 4.5 インスタンス変数のアクセス

* インスタンス変数は必ず `_変数名` とする
* 外部からのアクセスは `get_変数名()` / `set_変数名()` メソッド経由
* （Pythonicな `@property` でもOKだが、チームでスタイル統一）

```python
class Enemy:
    def __init__(self, hp: int):
        self._hp: int = hp

    def get_hp(self) -> int:
        return self._hp

    def set_hp(self, value: int) -> None:
        self._hp = max(0, value)
```

### 4.6 `core/constants.py` の書き方

担当ごとのセクションに分けて記述する：

```python
# core/constants.py
"""全プロジェクトで共有する定数。"""

# ===== 画面・描画（ベース） =====
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60

# ===== ゲームバランス（ベース） =====
INITIAL_GOLD: int = 100
CORE_MAX_HP: int = 1000

# ===== 進化AI（担当①） =====
NN_INPUT_SIZE: int = 12
NN_HIDDEN_SIZE: int = 16
NN_OUTPUT_SIZE: int = 2
GA_MUTATION_RATE: float = 0.05

# ===== ネットワーク（担当②） =====
NET_PORT: int = 50007
NET_STATE_HZ: int = 20
NET_TIMEOUT_SEC: float = 5.0

# ===== タワー（担当③） =====
FIRE_DAMAGE: int = 15
ICE_SLOW_FACTOR: float = 0.5
```

---

## 5. パターン別の実装ガイド

### 5.1 新しい敵クラスを追加するとき

1. **基底クラス**：`core/base_enemy.py` の `BaseEnemy` を継承
2. **配置場所**：
   - 進化対応敵 → `evolution/evolved_enemy.py`
   - ボス・特殊敵 → `combat/boss_enemy.py`, `combat/special_enemy.py`
3. **必須実装**：`update()`, `draw(screen)`, `take_damage(amount)`

### 5.2 新しいタワーを追加するとき

1. **基底クラス**：`core/base_tower.py` の `BaseTower` を継承
2. **配置場所**：`towers/<属性名>_tower.py`
3. **必須実装**：`attack(targets)`, `upgrade()`, `get_cost()`

### 5.3 ネットワークメッセージを追加するとき

1. **配置場所**：`network/net_protocol.py` にメッセージ型を追加
2. **シリアライズ**：JSON形式で `serialize_message(msg: dict) -> bytes`
3. **デシリアライズ**：`deserialize_message(data: bytes) -> dict`
4. **重要メッセージ**：`ack_required=True` を付けてACK＋再送機構に乗せる

### 5.4 効果音／BGMを再生するとき

```python
import pygame as pg
# 初期化（main.pyで1回だけ）
pg.mixer.init()

# 効果音
snd = pg.mixer.Sound("assets/sound/explosion.wav")
snd.play(maxtime=1000)  # 最大1秒

# BGM
pg.mixer.music.load("assets/sound/bgm.mp3")
pg.mixer.music.play(loops=-1)  # 無限ループ
pg.mixer.music.stop()
```

担当⑤の `presentation/sound_manager.py` で集中管理する。

---

## 6. Git運用ルール

### 6.1 ブランチ

* `main`：代表者のリポジトリにのみ存在、共通基本機能とマージ済み機能
* 機能ブランチ：`C0A25XXX/機能名` 形式（学籍番号は半角・大文字）
* 例：`C0A25001/evolution_ai`, `C0A25002/network_udp`

### 6.2 コミットメッセージ

* 日本語または英語、どちらでもよい（チームで統一）
* 動詞で始める：「追加」「修正」「リファクタ」など
* 例：
  - `feat: NN個体の交叉処理を追加`
  - `fix: 敵スポーン時の座標バグを修正`
  - `docs: READMEに分担追加機能の説明を追記`

### 6.3 プッシュとプル

* 機能ブランチへのpushはこまめに（毎日1回以上を目安）
* mainブランチが更新されたら、その都度自分のブランチに取り込む（`git pull origin main` してマージ）
* コンフリクトが起きたら、関係メンバーと相談しながら**手動で解消**（どちらか一方だけが正しいとは限らない）

### 6.4 .gitignore

```
__pycache__/
*.pyc
.vscode/
.DS_Store
*.log
```

---

## 7. テストの書き方

### 7.1 単体テストの配置

* 各パッケージ内に `test_<モジュール名>.py` を配置
* 例：`evolution/test_evolution.py`, `network/test_network.py`

### 7.2 実行方法

外部ライブラリを使わず、シンプルなassertで書く：

```python
# evolution/test_evolution.py
"""進化AIの単体テスト。

実行方法:
    python -m evolution.test_evolution
"""
from evolution.neural_net import NeuralNet


def test_neural_net_forward():
    """NNの順伝播が正しい形のテンソルを返すか。"""
    nn = NeuralNet(input_size=12, hidden_size=16, output_size=2)
    output = nn.forward([0.0] * 12)
    assert len(output) == 2
    assert all(-1.0 <= v <= 1.0 for v in output)
    print("[OK] test_neural_net_forward")


if __name__ == "__main__":
    test_neural_net_forward()
    print("All tests passed.")
```

### 7.3 ネットワーク系のテスト

* `net_server.py` と `net_client.py` を**同一PC上で2プロセス起動**してテストする
* `127.0.0.1` を使う

---

## 8. AIアシスタントへの追加指示

### 8.1 コード生成時の優先順位

1. **動くこと** > 凝った最適化
2. **読みやすさ** > 短さ
3. **チームの規約** > 一般的なPythonベストプラクティス
4. **既存コードとの一貫性** > 個別の理想形

### 8.2 提案するコードの形式

* 関数・クラスにはdocstringと型ヒントを必ず付ける
* 「なぜそうするのか」のコメントを重要な箇所に1〜2行入れる
* 動作確認の方法を簡潔に示す（テストコード例、または実行コマンド）

### 8.3 不明な点があるとき

* 推測でコードを生成せず、明確化のための質問を返す
* 特に「どのパッケージに置くべきか」が不明なときは確認する

### 8.4 評価項目を意識する

授業の採点項目（個人成果物15点満点）：
1. READMEの説明が適切か（0〜2点）
2. 基本機能と比較して十分な量のコードか（0〜4点）
3. コード内コメントが必要十分か（0〜2点）
4. 型ヒント・関数アノテーション・docstringが十分か（0〜2点）
5. コード規約が守られているか（0 or 2点）
6. 関数・クラスを定義・使用した可読性の高いコードか（0〜2点）
7. どこかのサイトの丸パクりでないか（0 or 1点）

→ AIが生成するコードはこの7項目を満たすことを意識する。

---

## 9. 参考リンク

* 授業資料：`docs/` 内のPDF（配布物）
* pygame公式ドキュメント：https://www.pygame.org/docs/
* NumPy公式：https://numpy.org/doc/
* Python型ヒント：https://docs.python.org/ja/3/library/typing.html

---

## 10. このファイルの更新について

このファイルは開発中に更新される可能性があります。重要な変更は代表者がチームに通知してください。
