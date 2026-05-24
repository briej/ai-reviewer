"""Direct test of Ollama AI analysis

This is an integration test that calls a local Ollama instance. It is
skipped by default unless the environment variable `RUN_OLLAMA_TESTS` is
set to "1". This prevents the test suite from hanging when Ollama is
not available.
"""
import os
import sys
import pytest

if os.getenv("RUN_OLLAMA_TESTS") != "1":
    skip_msg = (
        "Skipping integration test that calls Ollama unless "
        "RUN_OLLAMA_TESTS=1"
    )
    pytest.skip(skip_msg, allow_module_level=True)

sys.path.insert(0, '.')

from pathlib import Path
from src.cloud_client import analyze_with_ai

# Read a longer file
file_path = Path(__file__).parent / "ai_reviewer.py"
content = file_path.read_text(encoding="utf-8")

print(f"Analyzing {file_path.name} ({len(content.splitlines())} lines)...")
print("Sending request to Ollama...")

try:
    result = analyze_with_ai(
        file_path, 
        content, 
        [],  # No initial issues
        provider="ollama",
        model="llama3.2-vision:11b",
        timeout=10,
    )
    print("\n=== AI Response ===")
    print(f"Summary: {result.get('summary', 'N/A')}")
    print(f"Risk level: {result.get('review', {}).get('risk_level', 'N/A')}")
    print(f"Issues found: {len(result.get('issues', []))}")
    print(f"False positives: {len(result.get('false_positives', []))}")
    
    if result.get('issues'):
        print("\n=== Issues ===")
        for issue in result['issues'][:5]:
            sev = issue.get('severity', 'unknown')
            typ = issue.get('type')
            msg = issue.get('message', '')[:80]
            print(f"  [{sev}] {typ}: {msg}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()