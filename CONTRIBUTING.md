# コントリビューターガイド

このドキュメントは、このリポジトリで開発するときの操作方法をまとめたものです。

## 1. 最初にやること

このプロジェクトでは、Pythonの仮想環境として `venv` または `Conda` を使えます。
どちらか一方を選んでセットアップしてください。

リポジトリをクローンします。

```bash
git clone https://github.com/TomokiAkiyama06/ProjExD_Group09.git
cd ProjExD_Group09
```

### venvを使う場合

Pythonの仮想環境を作成します。

```bash
python -m venv .venv
```

Windowsの場合:

```bash
.venv\Scripts\activate
```

macOS / Linuxの場合:

```bash
source .venv/bin/activate
```

依存関係をインストールします。

```bash
pip install -r requirements.txt
```

### Condaを使う場合

Condaを使っている場合は、以下のように環境を作成します。

```bash
conda create -n projexd-group09 python=3.10
conda activate projexd-group09
```

依存関係をインストールします。

```bash
pip install -r requirements.txt
```

環境を終了する場合:

```bash
conda deactivate
```


## 2. 実行方法

1人プレイで起動する場合:

```bash
python main.py --solo
```

ホストとして起動する場合:

```bash
python main.py --host
```

クライアントとして接続する場合:

```bash
python main.py --client --ip=192.168.1.10
```

`--ip` にはホスト側PCのIPアドレスを指定します。

## 3. 開発の流れ

基本的な流れは以下です。

```txt
Issueを確認する
↓
作業ブランチを作る
↓
実装する
↓
Ruffや動作確認を行う
↓
commitする
↓
pushする
↓
Pull Requestを作る
```

## 4. ブランチの作り方

作業前に `main` を最新化します。

```bash
git checkout main
git pull origin main
```

作業用ブランチを作成します。

```bash
git checkout -b C0A25XXX/feature-name
```

例:

```bash
git checkout -b C0A25001/evolution-ai
git checkout -b C0A25002/network-udp
git checkout -b C0A25003/tower-upgrade
```

CIやドキュメントなど共通設定を変更する場合は、以下のような名前でもOKです。

```bash
git checkout -b chore/add-ci-ruff
git checkout -b docs/update-readme
```

## 5. コードを書くときのルール

- 関数・メソッドには型ヒントを書く
- クラス・関数・メソッドにはdocstringを書く
- `from xxx import *` は使わない
- マジックナンバーはなるべく定数にする
- `print()` のデバッグログを残したままcommitしない
- 自分の担当範囲外のファイルを勝手に大きく変更しない

特に `main.py` は授業要件に関わるため、変更するときは注意してください。

## 6. Ruffで品質チェックする

Ruffを実行します。

```bash
ruff check .
ruff format . --check
```

自動修正できるものを直す場合:

```bash
ruff check . --fix
```

ただし、`--fix` 後は必ず差分を確認してください。

```bash
git diff
```

## 7. Pythonファイルの構文チェック

Pythonファイルが構文的に壊れていないか確認します。

```bash
python -m compileall .
```

## 8. commit方法

変更内容を確認します。

```bash
git status
git diff
```

変更をステージします。

```bash
git add .
```

commitします。

```bash
git commit -m "feat: タワー強化処理を追加"
```

コミットメッセージ例:

```txt
feat: 新機能を追加
fix: 不具合を修正
docs: ドキュメントを更新
chore: CIや設定を追加
refactor: 挙動を変えずに整理
```

## 9. push方法

作業ブランチをpushします。

```bash
git push -u origin ブランチ名
```

例:

```bash
git push -u origin C0A25001/evolution-ai
```

## 10. Pull Requestの作り方

GitHub上で、pushしたブランチから `main` に向けてPull Requestを作成します。

PR本文には以下を書くとレビューしやすくなります。

```md
## 概要

- 何を変更したか

## 確認方法

- 実行したコマンド
- 確認した画面や動作

## 関連Issue

- close #番号
```

例:

```md
## 概要

- 炎タワーの攻撃処理を追加
- 攻撃範囲内の敵を探索する処理を追加

## 確認方法

- python main.py --solo
- ruff check .
- python -m compileall .

## 関連Issue

- close #12
```

## 11. PRを出す前の確認

PRを出す前に、最低限以下を確認してください。

```bash
ruff check .
python -m compileall .
python main.py --solo
```

確認できたら、PR本文に実行結果を書きます。

```md
## 確認方法

- [x] ruff check .
- [x] python -m compileall .
- [x] python main.py --solo
```

## 12. mainを直接編集しない

基本的に `main` ブランチへ直接pushしないでください。

必ず作業ブランチを作り、Pull Request経由で変更します。

## 13. コンフリクトしたとき

まず `main` を取り込みます。

```bash
git checkout main
git pull origin main
git checkout 自分のブランチ
git merge main
```

コンフリクトが出たら、該当ファイルを手動で修正します。

修正後:

```bash
git add .
git commit
git push
```

不安な場合は、無理に解決せずチームメンバーに相談してください。

## 14. 困ったとき

以下を確認してください。

- `README.md`
- `AGENTS.md`
- `docs/` 配下の設計資料
- GitHubのIssue
- Pull Requestのコメント

それでも分からない場合は、IssueやPRコメントで相談してください。
