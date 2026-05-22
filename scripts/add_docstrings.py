"""関数・メソッド・クラスに 1 行 docstring を一括挿入するヘルパスクリプト。

AGENTS.md §4.3「すべての関数・メソッド・クラスにdocstringを書く」に従って、
docstring が抜けている公開関数・メソッド・クラスへ 1 行 docstring を挿入する。
関数名のパターン（get_/set_/is_/has_/can_/add_/update/draw 等）から自動生成し、
推測できない場合は汎用テンプレートで埋める。

使い方:
    python -m scripts.add_docstrings <ファイル/ディレクトリ ...>

挿入後は ruff format で整形しなおすこと:
    ruff format <対象>
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# 関数名の接頭辞 → 1 行 docstring を生成するパターン
NAME_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^get_(.+)$"), "{name} を返す。"),
    (re.compile(r"^set_(.+)$"), "{name} を設定する。"),
    (re.compile(r"^add_(.+)$"), "{name} を追加する。"),
    (re.compile(r"^remove_(.+)$"), "{name} を削除する。"),
    (re.compile(r"^clear_(.*)$"), "{name} をクリアする。"),
    (re.compile(r"^reset_(.*)$"), "{name} を初期状態に戻す。"),
    (re.compile(r"^is_(.+)$"), "{name} かどうかを返す。"),
    (re.compile(r"^has_(.+)$"), "{name} を持つかどうかを返す。"),
    (re.compile(r"^can_(.+)$"), "{name} できるかどうかを返す。"),
    (re.compile(r"^update_(.+)$"), "{name} を更新する。"),
    (re.compile(r"^draw_(.+)$"), "{name} を描画する。"),
    (re.compile(r"^spawn_(.+)$"), "{name} エフェクトをスポーンする。"),
    (re.compile(r"^play_(.+)$"), "{name} を再生する。"),
    (re.compile(r"^stop_(.+)$"), "{name} を停止する。"),
    (re.compile(r"^start_(.+)$"), "{name} を開始する。"),
    (re.compile(r"^load_(.+)$"), "{name} を読み込む。"),
    (re.compile(r"^send_(.+)$"), "{name} を送信する。"),
    (re.compile(r"^receive_(.*)$"), "{name} を受信する。"),
    (re.compile(r"^handle_(.+)$"), "{name} を処理する。"),
    (re.compile(r"^check_(.+)$"), "{name} を判定する。"),
    (re.compile(r"^cycle_(.+)$"), "{name} を切り替える。"),
    (re.compile(r"^drain_(.+)$"), "{name} を取り出して内部キューを空にする。"),
    (re.compile(r"^consume_(.+)$"), "{name} を取り出して消費する。"),
    (re.compile(r"^find_(.+)$"), "{name} を探して返す。"),
    (re.compile(r"^request_(.+)$"), "{name} をリクエストする。"),
    (re.compile(r"^apply_(.+)$"), "{name} を適用する。"),
    (re.compile(r"^try_(.+)$"), "{name} を試行する。"),
]

# 関数名そのまま → docstring（接頭辞マッチで拾えない既知の関数）
EXACT_NAMES: dict[str, str] = {
    "update": "1 フレーム分の状態を更新する。",
    "draw": "Surface に描画する。",
    "run": "メインループを実行する。",
    "stop": "停止する。",
    "start": "開始する。",
    "close": "リソースを解放する。",
    "attack": "攻撃を行う。",
    "fire": "発射する。",
    "activate": "発動する。",
    "init": "初期化する。",
    "connect": "接続を確立する。",
    "disconnect": "接続を切断する。",
    "tick": "1 ティック分の処理を行う。",
    "step": "1 ステップ分の処理を行う。",
    "decide": "次の行動を決定する。",
    "forward": "順伝播を実行する。",
    "mutate": "個体に突然変異を適用する。",
    "crossover": "親 2 個体の重みを交叉して子個体を生成する。",
    "clone": "同じ重みを持つ独立したコピーを返す。",
    "copy": "同じ重みを持つ独立したコピーを返す。",
    "broadcast": "全クライアントへ送信する。",
}


def _capitalize_first(text: str) -> str:
    """先頭文字を大文字化する（ruff D403 対策）。"""
    if not text:
        return text
    return text[0].upper() + text[1:]


def generate_docstring(name: str) -> str:
    """関数名から 1 行 docstring を生成する。"""
    if name in EXACT_NAMES:
        return _capitalize_first(EXACT_NAMES[name])
    for pattern, template in NAME_PATTERNS:
        match = pattern.match(name)
        if match:
            inner = match.group(1) if match.groups() else name
            inner_label = inner if inner else name
            return _capitalize_first(template.format(name=inner_label))
    return _capitalize_first(f"{name} を行う。")


def _is_class_or_function(node: ast.AST) -> bool:
    """関数・非同期関数・クラスのいずれか。"""
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))


def find_missing(filepath: Path) -> list[tuple[int, int, str]]:
    """Docstring が抜けている公開定義の (挿入行, インデント, 名前) を返す。

    `__init__` / 単一アンダースコア接頭辞は対象外（監査と同じ基準）。
    """
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    results: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if not _is_class_or_function(node):
            continue
        if node.name.startswith("__"):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("_"):
            continue
        if ast.get_docstring(node):
            continue
        body = node.body
        if not body:
            continue
        first = body[0]
        results.append((first.lineno, first.col_offset, node.name))
    return results


def insert_docstrings(filepath: Path) -> int:
    """1 ファイルに対して必要な docstring を挿入する。

    Returns:
        挿入した docstring の個数。
    """
    missing = find_missing(filepath)
    if not missing:
        return 0
    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    # 後ろから挿入することで行番号がずれない
    missing.sort(key=lambda item: item[0], reverse=True)
    for body_lineno, body_col, name in missing:
        indent = " " * body_col
        docstring = generate_docstring(name)
        new_line = f'{indent}"""{docstring}"""\n'
        lines.insert(body_lineno - 1, new_line)
    filepath.write_text("".join(lines), encoding="utf-8")
    return len(missing)


def expand_targets(args: list[str]) -> list[Path]:
    """ファイル/ディレクトリの混在引数を *.py のリストに展開する。"""
    paths: list[Path] = []
    for arg in args:
        root = Path(arg)
        if root.is_file() and root.suffix == ".py":
            paths.append(root)
        elif root.is_dir():
            paths.extend(sorted(root.rglob("*.py")))
    # キャッシュ・venv・test_*.py を除外
    exclude_parts = {"__pycache__", ".venv", "venv", ".git"}
    return [
        path
        for path in paths
        if not any(part in exclude_parts for part in path.parts)
        and not path.name.startswith("test_")
    ]


def main() -> int:
    """エントリーポイント。"""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    targets = expand_targets(sys.argv[1:])
    total = 0
    for path in targets:
        added = insert_docstrings(path)
        if added:
            print(f"{path}: +{added}")
            total += added
    print(f"Total inserted: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
