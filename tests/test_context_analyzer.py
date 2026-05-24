"""Tests for ai-reviewer context analyzer module"""
import tempfile
from pathlib import Path

from src.context_analyzer import CodeGraph


def test_code_graph_detects_python_files():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "main.py").write_text("def main(): pass")
        (tmp_path / "utils.py").write_text("def helper(): pass")
        
        graph = CodeGraph(tmp_path)
        graph.scan_project()
        
        assert len(graph.nodes) == 2
        assert "main.py" in str(list(graph.nodes.keys())[0])


def test_code_graph_detects_functions():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "test.py").write_text("""
def foo():
    pass

def bar(x, y):
    pass
""")
        
        graph = CodeGraph(tmp_path)
        graph.scan_project()
        
        # Check functions were detected
        assert any("test.py" in str(k) for k in graph.functions.keys())


def test_code_graph_detects_project_type():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")
        
        graph = CodeGraph(tmp_path)
        graph.scan_project()
        
        context = graph.get_context_for_file("app.py")
        assert context["project_type"] == "web-application"


def test_code_graph_finds_entry_points():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "main.py").write_text("""
def main():
    pass

if __name__ == "__main__":
    main()
""")
        
        graph = CodeGraph(tmp_path)
        graph.scan_project()
        
        entry_points = graph.find_entry_points()
        assert any("main" in ep for ep in entry_points)