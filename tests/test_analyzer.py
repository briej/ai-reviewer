"""Tests for ai-reviewer analyzer module"""
from pathlib import Path

from src.analyzer import fast_analyze


def test_detects_hardcoded_password():
    code = 'password = "secret123"'
    issues = fast_analyze(Path("config.py"), code)
    assert any(i["type"] == "hardcoded-secret" for i in issues)


def test_detects_sql_injection():
    code = 'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")'
    issues = fast_analyze(Path("db.py"), code)
    assert any(i["type"] == "sql-injection" for i in issues)


def test_detects_eval():
    code = "result = eval(user_input)"
    issues = fast_analyze(Path("app.py"), code)
    assert any(i["type"] == "code-injection" for i in issues)


def test_detects_weak_hash():
    code = "import hashlib\nhashlib.md5(data)"
    issues = fast_analyze(Path("auth.py"), code)
    assert any(i["type"] == "weak-crypto" for i in issues)


def test_detects_debug_mode():
    code = "DEBUG = True"
    issues = fast_analyze(Path("settings.py"), code)
    assert any(i["type"] == "debug-enabled" for i in issues)


def test_clean_code_has_no_issues():
    code = "def hello():\n    print('hi')"
    issues = fast_analyze(Path("hello.py"), code)
    assert len(issues) == 0
