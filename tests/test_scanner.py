"""Tests for ai-reviewer scanner module"""
import tempfile
from pathlib import Path

from src.scanner import scan_files, read_file


def test_scan_files_finds_python():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "main.py").write_text("x = 1")
        Path(tmp, "test.js").write_text("const x = 1")
        files = scan_files(tmp, ignore_patterns=set())
        names = [f.name for f in files]
        assert "main.py" in names
        assert "test.js" in names


def test_scan_files_ignores_pycache():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "main.py").write_text("x = 1")
        Path(tmp, "__pycache__").mkdir()
        Path(tmp, "__pycache__", "cached.pyc").write_text("")
        files = scan_files(tmp, ignore_patterns={"__pycache__"})
        names = [f.name for f in files]
        assert "main.py" in names
        assert "cached.pyc" not in names


def test_read_file_returns_content():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp, "test.py")
        f.write_text("hello world", encoding="utf-8")
        assert read_file(f) == "hello world"


def test_read_file_skips_large_files():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp, "big.py")
        f.write_text("x" * (20 * 1024 * 1024))  # 20 MB
        assert read_file(f, max_size_mb=10) is None
