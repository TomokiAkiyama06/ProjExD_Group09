# Issues for Claude Code

このディレクトリには、本プロジェクトで作成すべきGitHubイシューが**1イシュー1ファイル**で格納されています。Claude Codeがこのディレクトリを読み込んでイシューを順次作成することを想定しています。

## ファイル命名規則

```
<番号3桁>_<種別>_<短い説明>.md
```

- 番号は登録順（Epic→Taskの順）
- 種別は `epic` または `task`
- 例：`001_epic_meta.md`, `005_task_main_py_skeleton.md`

## ファイル形式

各ファイルはYAMLフロントマター（メタ情報）+ 本文の構成です。

```markdown
---
title: "イシューのタイトル"
labels: ["epic", "core", "priority:high"]
assignees: []
milestone: null
parent: null  # Epic の場合は null、Task の場合は親Epicのファイル名
depends_on: []  # 依存するTaskのファイル名（あれば）
---

# 本文（Markdown）
```

## ファイル一覧

### Epic (8件)

- `001_epic_meta.md` — プロジェクト全体管理
- `002_epic_setup.md` — 初期セットアップ
- `008_epic_core_package.md` — 共通基本機能：core パッケージ
- `017_epic_solo_mode.md` — 共通基本機能：soloモード
- `021_epic_evolution_ai.md` — 担当①：進化AI
- `030_epic_network.md` — 担当②：UDPネットワーク
- `040_epic_towers.md` — 担当③：タワー属性とアップグレード
- `047_epic_combat.md` — 担当④：前線戦闘と演出
- `056_epic_presentation.md` — 担当⑤：対戦・可視化・サウンド

### Task (約57件)

`003_task_*.md` から `064_task_*.md` まで。

## Claude Code への指示例

```
このディレクトリにある .md ファイルを番号順に読み込み、
それぞれの内容で GitHub Issue を作成してください。

- フロントマターの title をイシューのタイトルに
- フロントマターの labels を GitHub のラベルに（存在しなければラベルも作成）
- 本文部分をイシューの本文に
- Epic の場合は親イシュー、Task の場合は親 Epic のイシュー番号を本文に追記
- depends_on は本文末尾に「依存: #XX」として追記

なお、リポジトリは TomokiAkiyama06/ProjExD_Group09 です。
```

または `gh` CLI で実行する例：

```bash
# ラベルを先に作成
gh label create epic --color "5319E7" --description "大タスク"
gh label create task --color "0052CC" --description "タスク"
gh label create core --color "1D76DB"
gh label create evolution --color "FBCA04"
gh label create network --color "D93F0B"
gh label create towers --color "0E8A16"
gh label create combat --color "B60205"
gh label create presentation --color "F9D0C4"
gh label create infra --color "BFD4F2"
gh label create meta --color "C2E0C6"
gh label create "priority:high" --color "B60205"
gh label create "priority:mid" --color "FBCA04"
gh label create "priority:low" --color "C5DEF5"

# 各イシューを順番に登録
for f in $(ls *.md | grep -v README | sort); do
  title=$(grep '^title:' "$f" | sed 's/title: *"\(.*\)"/\1/')
  labels=$(grep '^labels:' "$f" | sed 's/labels: *//;s/\[//;s/\]//;s/"//g;s/, */,/g')
  body=$(sed -n '/^---$/,/^---$/!p' "$f" | sed '1d')
  echo "Creating: $title"
  gh issue create --title "$title" --label "$labels" --body "$body"
done
```

## イシューの構成・粒度

- **Epic**：機能の大単位。1人の担当者の責務範囲。チェックリストで配下のTaskを束ねる。
- **Task**：1人が半日（3〜4時間）以内に完了できる作業単位。コミット1回で済むのが理想。

合計：Epic 8件 + Task 約57件
