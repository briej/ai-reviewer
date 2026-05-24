"""AI-powered analysis (Ollama and Cloud providers)"""
import json
from pathlib import Path
from typing import List, Dict, Any

from .analyzer import fast_analyze


try:
    from cloud_client import CloudClient
    CLOUD_AVAILABLE = True
except ImportError:
    CLOUD_AVAILABLE = False


def ai_analyze(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Analyze via local Ollama (placeholder)."""
    console = __import__("rich.console", fromlist=["Console"]).Console()
    console.print("[yellow]⚠️  AI mode requires Ollama. Falling back to fast mode.[/yellow]")
    return fast_analyze(file_path, content)


def cloud_analyze(
    file_path: Path,
    content: str,
    provider: str,
    api_key: str,
    model: str = "",
) -> List[Dict[str, Any]]:
    """Analyze via cloud AI provider.
    
    Args:
        file_path: Path to file.
        content: File contents.
        provider: Provider name (deepseek, openrouter, etc.).
        api_key: API key.
        model: Specific model (optional).
    
    Returns:
        List of issues.
    """
    # Validate provider name (prevent IDOR)
    VALID_PROVIDERS = {"ollama", "deepseek", "openrouter", "groq", "kimi", "qwen"}
    if provider not in VALID_PROVIDERS:
        raise ValueError(f"Invalid provider: {provider}. Must be one of: {', '.join(VALID_PROVIDERS)}")
    
    if not CLOUD_AVAILABLE:
        return fast_analyze(file_path, content)
    
    try:
        client = CloudClient(provider, api_key, model)
        
        prompt = f"""Analyze this {file_path.suffix.replace('.', '')} code for bugs and security issues.

Find:
1. CRITICAL: Bugs, vulnerabilities, security issues
2. WARNING: Code smells, bad practices  
3. INFO: Improvements, optimizations

Code:
```{file_path.suffix.replace('.', '')}
{content[:10000]}
```

Return ONLY a JSON array:
[
  {{"severity": "critical", "type": "security", "message": "description"}},
  ...
]"""
        
        response = client.chat(prompt)
        
        # Parse JSON from response
        issues: List[Dict[str, Any]] = []
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                ai_issues = json.loads(json_str)
                for issue in ai_issues:
                    issues.append({
                        "severity": issue.get("severity", "info"),
                        "type": issue.get("type", "ai-detected"),
                        "location": file_path.name,
                        "message": issue.get("message", "Issue detected"),
                    })
        except json.JSONDecodeError:
            console = __import__("rich.console", fromlist=["Console"]).Console()
            console.print(
                f"[yellow]⚠️  Could not parse AI response for {file_path.name}, using fast mode[/yellow]"
            )
            return fast_analyze(file_path, content)
        
        return issues
    
    except Exception as e:
        console = __import__("rich.console", fromlist=["Console"]).Console()
        console.print(f"[red]❌ Cloud mode error: {e}[/red]")
        console.print("[dim]Falling back to fast mode[/dim]")
        return fast_analyze(file_path, content)
