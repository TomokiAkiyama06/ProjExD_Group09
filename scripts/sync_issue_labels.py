"""GitHub Issueラベルを定義ファイルから作成・更新するスクリプト。

使い方:
    python scripts/sync_issue_labels.py --repo owner/name --token YOUR_TOKEN
    python scripts/sync_issue_labels.py --repo owner/name --token YOUR_TOKEN --dry-run

環境変数から読む場合:
    GITHUB_TOKEN=xxx python scripts/sync_issue_labels.py --repo owner/name
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

LABELS_FILE = Path(__file__).resolve().parents[1] / ".github" / "issue-labels.json"
API_BASE_URL = "https://api.github.com"


def load_labels() -> list[dict[str, str]]:
    """ラベル定義ファイルを読み込む。"""
    with LABELS_FILE.open("r", encoding="utf-8") as file:
        labels = json.load(file)

    if not isinstance(labels, list):
        raise ValueError("ラベル定義は配列である必要があります。")

    return labels


def request_github(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any] | None]:
    """GitHub APIへリクエストを送る。"""
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        parsed = json.loads(body) if body else None
        return error.code, parsed


def create_or_update_label(repo: str, token: str, label: dict[str, str], dry_run: bool) -> None:
    """ラベルを作成し、既に存在する場合は更新する。"""
    name = label["name"]
    payload = {
        "name": name,
        "color": label["color"],
        "description": label.get("description", ""),
    }

    if dry_run:
        print(f"[DRY-RUN] sync label: {name}")
        return

    create_url = f"{API_BASE_URL}/repos/{repo}/labels"
    status, body = request_github("POST", create_url, token, payload)

    if status == 201:
        print(f"[CREATE] {name}")
        return

    already_exists = status == 422 and body and "already_exists" in json.dumps(body)
    if not already_exists:
        print(f"[ERROR] failed to create {name}: status={status}, body={body}", file=sys.stderr)
        return

    encoded_name = urllib.parse.quote(name, safe="")
    update_url = f"{API_BASE_URL}/repos/{repo}/labels/{encoded_name}"
    status, body = request_github("PATCH", update_url, token, payload)

    if status == 200:
        print(f"[UPDATE] {name}")
        return

    print(f"[ERROR] failed to update {name}: status={status}, body={body}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(description="GitHub Issueラベルを同期する")
    parser.add_argument("--repo", required=True, help="owner/name 形式のリポジトリ名")
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub Personal Access Token",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には作成・更新せず内容だけ表示する",
    )
    return parser.parse_args()


def main() -> None:
    """ラベル同期処理のエントリーポイント。"""
    args = parse_args()
    if not args.token and not args.dry_run:
        raise ValueError("--token または GITHUB_TOKEN が必要です。")

    labels = load_labels()
    for label in labels:
        create_or_update_label(args.repo, args.token or "", label, args.dry_run)


if __name__ == "__main__":
    main()
