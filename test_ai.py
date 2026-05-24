"""Test AI analysis with Ollama"""
from pathlib import Path
from src.ai_analyzer import ai_analyze

content = 'password = "secret123"'
print("Testing ai_analyze...")
issues = ai_analyze(Path("test.py"), content)
print(f"Found {len(issues)} issues:")
for issue in issues:
    print(f"  - {issue}")
