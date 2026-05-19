# Issueラベル作成手順

このリポジトリでは、Issueテンプレートで使うラベルを `.github/issue-labels.json` に定義している。

## なぜ必要か

GitHub Issue Forms の `labels` は、リポジトリに同名ラベルが存在する場合だけ自動付与される。
そのため、Issueテンプレートを有効にするだけではラベルは作成されない。

## 作成・更新方法

GitHubのPersonal Access Tokenを用意して、以下を実行する。

```bash
GITHUB_TOKEN=your_token python scripts/sync_issue_labels.py --repo Project-Practice2026/ProjExD_Group0X
```

事前確認だけしたい場合は `--dry-run` を付ける。

```bash
python scripts/sync_issue_labels.py --repo Project-Practice2026/ProjExD_Group0X --dry-run
```

## 必要な権限

Personal Access Token には、このリポジトリのIssueラベルを作成・更新できる権限が必要。

Fine-grained tokenを使う場合は、対象リポジトリに対して以下の権限を付ける。

- Repository access: `Project-Practice2026/ProjExD_Group0X`
- Issues: Read and write
- Metadata: Read-only

## 追加されるラベル

ラベル一覧は以下を参照する。

- `.github/issue-labels.json`
- `docs/ISSUE_LABELS.md`

## 注意

- ラベル名はIssueテンプレート内の `labels` と完全一致させる必要がある
- 既に同名ラベルがある場合は、色と説明が更新される
- 不要な既存ラベルの削除はこのスクリプトでは行わない
