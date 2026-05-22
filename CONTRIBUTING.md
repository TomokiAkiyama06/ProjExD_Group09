# コントリビューターガイド

このドキュメントは、このリポジトリで開発するときの操作方法をまとめたものです。

## 1. 最初にやること

このプロジェクトでは、実行方法を `Conda` または `uv` のどちらかにそろえます。
自分が使いやすい方法を1つ選んでセットアップしてください。

リポジトリをクローンします。

```bash
git clone https://github.com/TomokiAkiyama06/ProjExD_Group09.git
cd ProjExD_Group09
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

### uvを使う場合

`uv` を使う場合は、以降の実行例のように `requirements.txt` を指定して実行します。
環境作成と依存関係の解決は `uv run` 側で行います。

`uv` が使えるか確認します。

```bash
uv --version
```

## 2. 実行方法

### Condaで実行する場合

1人プレイで起動する場合:

```bash
conda run -n projexd-group09 python main.py --solo
```

ホストとして起動する場合:

```bash
conda run -n projexd-group09 python main.py --host
```

クライアントとして接続する場合:

```bash
conda run -n projexd-group09 python main.py --client --ip=192.168.1.10
```

### uvで実行する場合

1人プレイで起動する場合:

```bash
uv run --with-requirements requirements.txt main.py --solo
```

ホストとして起動する場合:

```bash
uv run --with-requirements requirements.txt main.py --host
```

クライアントとして接続する場合:

```bash
uv run --with-requirements requirements.txt main.py --client --ip=192.168.1.10
```

`--ip` にはホスト側PCのIPアドレスを指定します。

## 3. 機能実装の流れ（Git初心者向け）

このプロジェクトでは、共有用の `main` ブランチに直接機能を追加せず、
機能ごとの作業ブランチで実装してからPull Request（PR）で取り込みます。

Gitの操作は、最初は以下の意味だけ押さえておけば進められます。

| 操作 | 意味 |
|------|------|
| `git status` | 今いるブランチと、変更したファイルを確認する |
| `git diff` | ファイルの変更内容を確認する |
| `git add` | commitに入れたい変更を選ぶ |
| `git commit` | 変更の区切りを自分のPCに記録する |
| `git push` | commitをGitHubに送る |
| Pull Request | `main` に取り込んでよいかレビューをお願いする |

### 3.1 作業の全体像

機能を実装するときは、基本的に次の順番で進めます。

```txt
Issueを確認する
↓
作業ブランチを確認する
↓
コードを書く
↓
動作確認と品質チェックを行う
↓
変更内容を確認する
↓
commitする
↓
pushする
↓
Pull Requestを作る
↓
レビューで指摘があれば同じブランチで直す
```

### 3.2 作業前にIssueと担当範囲を確認する

まず、GitHubのIssueで次を確認します。

- 何を作るIssueか
- どのファイルやパッケージを触るIssueか
- 他のIssueや機能に依存していないか

このリポジトリでは担当範囲が分かれています。
自分の担当外のパッケージ、特に `core/` を変更したくなった場合は、
実装を進める前にチームメンバーへ相談してください。

### 3.3 今いるブランチを確認する

コードを書き始める前に、必ず現在地を確認します。

```bash
git status
git branch --show-current
```

表示されたブランチ名が、今進めるIssue用の作業ブランチならそのまま進めてOKです。
この場合、同じブランチを作り直す必要はありません。

ブランチ名が `main` の場合は、機能実装を始める前に作業ブランチを作ります。
作り方は「4. ブランチの作り方」を参照してください。

`git status` に自分がまだ把握していない変更が表示された場合は、
消したりcommitしたりする前に、誰の変更か確認してください。

### 3.4 コードを書く

Issueの内容に合わせて、必要なファイルだけを変更します。
大きな機能でも、最初から全部書き切ろうとせず、動く区切りごとに確認すると進めやすいです。

作業中は、ときどき次を実行して変更を確認します。

```bash
git status
git diff
```

`git diff` で表示される内容は、まだcommitしていない変更です。
意図しないファイルが混ざっていないか確認してください。

### 3.5 動作確認と品質チェックを行う

実装が一区切りついたら、使っている実行方法で最低限次を確認します。

Condaの場合:

```bash
conda run -n projexd-group09 ruff check .
conda run -n projexd-group09 python -m compileall .
conda run -n projexd-group09 python main.py --solo
```

uvの場合:

```bash
uv run --with-requirements requirements.txt ruff check .
uv run --with-requirements requirements.txt -m compileall .
uv run --with-requirements requirements.txt main.py --solo
```

フォーマットも確認する場合は、使っている実行方法に合わせて次を実行します。

```bash
conda run -n projexd-group09 ruff format . --check
```

```bash
uv run --with-requirements requirements.txt ruff format . --check
```

ネットワーク機能など `--solo` だけでは確認できない機能は、
IssueやPR本文に、実際に確認した手順を書いてください。

### 3.6 commitする

commit前に、まず変更内容を確認します。

```bash
git status
git diff
```

commitに入れたいファイルを選びます。
初心者のうちは、関係するファイルを指定して `git add` すると混ざりにくいです。

```bash
git add 変更したファイル名
```

例:

```bash
git add evolution/evolution_manager.py
git add evolution/test_evolution.py
```

変更がすべて今回の機能に関係していると確認できた場合は、次でも構いません。ただし、不要なファイルも一緒にコミットする可能性があるので、どうしても必要でない限り使用しないようにしてください。

```bash
git add .
```

その後、commitします。

```bash
git commit -m "feat: 突然変異率の調整処理を追加"
```

commitは「作業が全部終わるまで1回だけ」にする必要はありません。
意味のある区切りごとに記録しておくと、後で見返しやすくなります。

### 3.7 GitHubへpushする

最初のpushでは、ブランチ名を指定します。

```bash
git push -u origin ブランチ名
```

例:

```bash
git push -u origin C0A25001/evolution-ai
```

同じブランチを2回目以降にpushするときは、通常は次で送れます。

```bash
git push
```

### 3.8 Pull Requestを作る

GitHub上で、作業ブランチから `main` に向けてPRを作ります。
PRには「何を変えたか」と「どう確認したか」を書きます。

PRを出した後に修正が必要になっても、新しいブランチを作り直す必要はありません。
同じ作業ブランチで修正し、もう一度commitしてpushするとPRに反映されます。

### 3.9 迷ったときの確認順

Gitの操作が分からなくなったら、まず次の順番で確認してください。

1. `git status` で今いるブランチと変更ファイルを見る
2. `git diff` で変更内容を見る
3. 今回のIssueに関係する変更だけか確認する
4. 不安な場合はcommitやpushの前にチームメンバーへ相談する

## 4. ブランチの作り方

まだ作業ブランチがない場合は、作業前に `main` を最新化します。

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

使っている実行方法に合わせてRuffを実行します。

Condaの場合:

```bash
conda run -n projexd-group09 ruff check .
conda run -n projexd-group09 ruff format . --check
```

uvの場合:

```bash
uv run --with-requirements requirements.txt ruff check .
uv run --with-requirements requirements.txt ruff format . --check
```

自動修正できるものを直す場合:

```bash
conda run -n projexd-group09 ruff check . --fix
```

```bash
uv run --with-requirements requirements.txt ruff check . --fix
```

ただし、`--fix` 後は必ず差分を確認してください。

```bash
git diff
```

## 7. Pythonファイルの構文チェック

Pythonファイルが構文的に壊れていないか確認します。

Condaの場合:

```bash
conda run -n projexd-group09 python -m compileall .
```

uvの場合:

```bash
uv run --with-requirements requirements.txt -m compileall .
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

- uv run --with-requirements requirements.txt main.py --solo
- uv run --with-requirements requirements.txt ruff check .
- uv run --with-requirements requirements.txt -m compileall .

## 関連Issue

- close #12
```

## 11. PRを出す前の確認

PRを出す前に、使っている実行方法で最低限以下を確認してください。

Condaの場合:

```bash
conda run -n projexd-group09 ruff check .
conda run -n projexd-group09 python -m compileall .
conda run -n projexd-group09 python main.py --solo
```

uvの場合:

```bash
uv run --with-requirements requirements.txt ruff check .
uv run --with-requirements requirements.txt -m compileall .
uv run --with-requirements requirements.txt main.py --solo
```

確認できたら、PR本文に実行結果を書きます。

```md
## 確認方法

- [x] uv run --with-requirements requirements.txt ruff check .
- [x] uv run --with-requirements requirements.txt -m compileall .
- [x] uv run --with-requirements requirements.txt main.py --solo
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
