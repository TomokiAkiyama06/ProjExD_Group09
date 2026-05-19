# Issue運用ルール

このドキュメントでは、Issueテンプレートとラベルの使い分けを定義する。

## Issue種別

| 種別 | 用途 |
| --- | --- |
| Epic | 大きな機能・テーマを管理する親Issue |
| Story | ユーザー視点の価値を表すIssue |
| Task | 実装作業・環境構築・CI整備など |
| Bug | 不具合報告・修正 |
| Experiment | 検証・調査・技術選定・設計検討 |
| Docs | README・仕様書・設計メモなどの整備 |

## 推奨ラベル

### 種別ラベル

- `type: epic`
- `type: story`
- `type: task`
- `type: bug`
- `type: experiment`
- `type: docs`

### 領域ラベル

- `area: core`
- `area: evolution`
- `area: network`
- `area: towers`
- `area: combat`
- `area: presentation`
- `area: dev-env`
- `area: infra`
- `area: ci`
- `area: docs`
- `area: ux`

### 優先度ラベル

- `priority: high`
- `priority: medium`
- `priority: low`

### 状態ラベル

- `status: needs-discussion`
- `status: ready`
- `status: in-progress`
- `status: blocked`
- `status: review`

### サイズラベル

- `size: xs`
- `size: s`
- `size: m`
- `size: l`

`size: l` が付いたTaskは分割を検討する。

## 運用方針

- Epic は親Issueとして使う
- Story はユーザー視点の価値を書く
- Task は1PRで終わる粒度にする
- 環境構築は `Task` + `area: dev-env` / `area: infra` / `area: ci` で管理する
- 調査・検証は `Experiment` に分ける
- READMEや手順整理は `Docs` に分ける
- PRは基本的に `Task` または `Bug` に紐づける

## 例

```txt
[Epic] LAN協力プレイ機能
  ├─ [Story] プレイヤーが同じLAN内で接続できる
  │    ├─ [Task] UDPサーバーを実装する
  │    ├─ [Task] クライアント接続処理を実装する
  │    └─ [Task] 接続状態の表示を追加する
  └─ [Experiment] LAN環境で通信遅延を検証する
```
