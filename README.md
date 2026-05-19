# 共進化の砦（仮）

> 2人協力プレイのタワーディフェンス。敵はニューラルネットを持ち、世代を経るごとにプレイヤーのタワー配置を学習して経路を最適化してくる。プレイヤー2人は別々のPCからLAN接続して「建築役」と「前線役」に役割分担し、敵の進化を出し抜く戦略を練る。

## 実行環境の必要条件

* python >= 3.10
* pygame >= 2.1
* numpy >= 1.24
* Ruff（`requirements.txt` からインストール）

依存関係は `requirements.txt` に統一しています。初回セットアップ時は以下を実行してください。

```bash
pip install -r requirements.txt
```

## ゲームの概要

* 2人協力プレイ対応のLANネットワークタワーディフェンスゲーム
* 敵は遺伝的ニューラルネットによって世代ごとに進化し、プレイヤーの戦法に適応してくる
* プレイヤー1は「建築役」（マウスでタワー設置）、プレイヤー2は「前線役」（キャラを操作して直接戦闘）
* ウェーブ制で進行し、規定ウェーブを生き残れば勝利、拠点HPが0で敗北
* 追加機能として、互いに敵を送り込み合う対戦モードも搭載

### 起動方法

```bash
# ホスト（プレイヤー1）として起動
python main.py --host

# クライアント（プレイヤー2）として起動
python main.py --client --ip=192.168.1.10

# 1人プレイ（フォールバック・デバッグ用）
python main.py --solo

```

## CI・品質チェック

このリポジトリでは GitHub Actions によるCIを追加しています。`main` へのpush時と、`main` 向けPull Request作成・更新時に以下を実行します。

* `ruff check . --output-format=github`
* `ruff format . --check`
* `python -m compileall .`
* リポジトリ内の `test_*.py` を簡易テストランナーで実行

Pull Requestを出す前に、ローカルでも以下を実行して確認してください。

```bash
ruff check .
ruff format . --check
python -m compileall .
python - <<'PY'
from pathlib import Path
import runpy
import sys

repo_root = Path(".").resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

test_files = sorted(Path(".").rglob("test_*.py"))

if not test_files:
    print("No test_*.py files found. Skipping simple test runner.")
    raise SystemExit(0)

for path in test_files:
    if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
        continue
    print(f"Running {path}")
    namespace = runpy.run_path(str(path), run_name="__main__")
    test_functions = [
        value
        for name, value in sorted(namespace.items())
        if name.startswith("test_") and callable(value)
    ]
    for test_function in test_functions:
        test_function()
PY
```

## 操作方法

### プレイヤー1（建築役・ホスト）
* マウス左クリック：タワー設置
* マウス右クリック：タワー選択 → アップグレード／売却
* 数字キー 1〜4：設置するタワー種類の切替（炎／氷／雷／物理）
* スペースキー：次ウェーブを早期開始

### プレイヤー2（前線役・クライアント）
* WASD：キャラ移動
* J：通常攻撃
* K：特殊スキル（クールタイムあり）
* L：タワー修理（近接時、リソース消費）
* Shift：ダッシュ

## ゲームの実装

### 共通基本機能

* 画面・マップ描画と拠点表示
* プレイヤー1・2の基本操作（タワー設置、キャラ移動、通常攻撃）
* 1種類のタワー設置と弾の発射
* 敵の出現と直進移動（NN未搭載の固定動作）
* ウェーブ管理の最低限の枠組み
* 共有リソース（エナジー）の管理
* HUDの基本表示（HP・リソース・ウェーブ番号）
* soloモード（1台で2プレイヤー操作、テスト・デバッグ用）

### 分担追加機能

* **進化NNによる敵移動システム（担当：XXX）** ：敵が個別に小さなニューラルネットを持ち、遺伝的アルゴリズムによりウェーブごとに進化する機能。NumPyのみで実装し、敵の経路選択を世代を経るごとに最適化する
* **LANネットワーク通信（担当：XXX）** ：UDPによる権威サーバ型のクライアント-サーバ通信機能。ホストがゲームロジックを保持し、20Hzで状態同期、30Hzで操作受信、重要イベントはACK＋再送で確実に伝達する
* **タワー属性・アップグレードシステム（担当：XXX）** ：炎／氷／雷／物理の4属性タワーと、レベルアップ機能。属性ごとに敵への効果が異なり、戦略性を生む
* **前線プレイヤー武器・スキル＋特殊敵・ボス・エフェクト（担当：XXX）** ：複数武器の切替、特殊スキル、ボス敵・特殊敵の追加、パーティクルエフェクト
* **対戦モード＋進化可視化＋HUD拡張＋サウンド（担当：XXX）** ：互いに敵を送り合う対戦モード、世代ごとの適応度グラフ、詳細HUD、BGM・効果音

### ToDo

- [ ] 進化AIの適応度関数のパラメータ調整
- [ ] ネットワーク同期のラグ補正
- [ ] 対戦モードのバランス調整

### メモ

* クラス内のインスタンス変数は、すべて `_変数名` のように先頭にアンダースコアを付け、外部アクセスは `get_変数名()` / `set_変数名()` メソッドを介して行う設計とする
* すべてのクラスに関係する関数は、各パッケージの `__init__.py` ではなく、関連するモジュール内のクラス外で定義する
* `main.py` の冒頭には必ず `os.chdir(os.path.dirname(os.path.abspath(__file__)))` を記述する
* 詳細な設計方針・クラス設計・ネットワークプロトコルは `docs/DESIGN.md` を参照
* コード規約・ディレクトリルール・AI支援開発のガイドラインは `AGENTS.md` を参照
