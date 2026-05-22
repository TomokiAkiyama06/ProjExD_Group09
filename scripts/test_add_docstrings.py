from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.add_docstrings import insert_docstrings


def _write_sample(tmp_dir: str, source: str) -> Path:
    path = Path(tmp_dir) / "sample.py"
    path.write_text(source, encoding="utf-8")
    return path


def test_insert_docstrings_expands_single_line_function() -> None:
    with TemporaryDirectory() as tmp_dir:
        path = _write_sample(tmp_dir, 'def get_value(item: dict[str, int]): return item["x"]\n')

        assert insert_docstrings(path) == 1
        result = path.read_text(encoding="utf-8")

        assert result == (
            'def get_value(item: dict[str, int]):\n    """Value を返す。"""\n    return item["x"]\n'
        )
        compile(result, str(path), "exec")


def test_insert_docstrings_expands_single_line_method() -> None:
    with TemporaryDirectory() as tmp_dir:
        path = _write_sample(
            tmp_dir,
            'class Example:\n    """Already documented."""\n\n    def bar(self): return 1\n',
        )

        assert insert_docstrings(path) == 1
        result = path.read_text(encoding="utf-8")

        assert result == (
            'class Example:\n    """Already documented."""\n\n'
            "    def bar(self):\n"
            '        """Bar を行う。"""\n'
            "        return 1\n"
        )
        compile(result, str(path), "exec")


def test_insert_docstrings_handles_class_with_single_line_method() -> None:
    with TemporaryDirectory() as tmp_dir:
        path = _write_sample(tmp_dir, "class Example:\n    def get_value(self): return 1\n")

        assert insert_docstrings(path) == 2
        result = path.read_text(encoding="utf-8")

        assert result == (
            "class Example:\n"
            '    """Example を行う。"""\n'
            "    def get_value(self):\n"
            '        """Value を返す。"""\n'
            "        return 1\n"
        )
        compile(result, str(path), "exec")


if __name__ == "__main__":
    test_insert_docstrings_expands_single_line_function()
    test_insert_docstrings_expands_single_line_method()
    test_insert_docstrings_handles_class_with_single_line_method()
    print("All add_docstrings tests passed.")
