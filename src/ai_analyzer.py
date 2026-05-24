"""AI-powered analysis (Ollama and Cloud providers) with context awareness"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .analyzer import fast_analyze
from .context_analyzer import CodeGraph

# Direct imports from cloud_client
from .cloud_client import (
    CloudClient,
    analyze_with_ai,
    _format_prompt,
    _detect_language,
    AIError,
)

CLOUD_AVAILABLE = True


def ai_analyze(
    file_path: Path,
    content: str,
    context: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """Analyze via local Ollama with context awareness.
    
    Args:
        file_path: Path to file.
        content: File contents.
        context: Project context from CodeGraph.
        use_cache: Use result caching for speed.
    
    Returns:
        List of issues with improved accuracy.
    """
    console = __import__("rich.console", fromlist=["Console"]).Console()
    
    # Quick pre-check: if file is trivial, skip AI
    if len(content.splitlines()) < 5:
        console.print(f"[dim]Skipping AI for short file: {file_path.name}[/dim]")
        return fast_analyze(file_path, content)
    
    # Get preliminary issues from static analysis
    initial_issues = fast_analyze(file_path, content)
    
    console.print(f"[cyan]Running AI analysis on {file_path.name}...[/cyan]")
    
    # Format enhanced prompt with context
    prompt = _format_prompt(file_path, content, initial_issues, context)
    
    try:
        # Try Ollama first (local, free)
        if not CLOUD_AVAILABLE:
            raise Exception("Cloud client not available")
        result = analyze_with_ai(
            file_path, content, initial_issues,
            provider="ollama",
            model="llama3.2-vision:11b",
            timeout=120,
        )
        
        console.print(f"[green]✓ AI analysis complete[/green]")
        
        # Process AI results
        return _process_ai_results(file_path, result, initial_issues)
        
    except Exception as e:
        console.print(f"[yellow]⚠️  AI analysis failed: {e}[/yellow]")
        console.print("[dim]Falling back to fast mode[/dim]")
        return fast_analyze(file_path, content)


def cloud_analyze(
    file_path: Path,
    content: str,
    provider: str,
    api_key: str,
    model: str = "",
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Analyze via cloud AI provider with context awareness.
    
    Args:
        file_path: Path to file.
        content: File contents.
        provider: Provider name (deepseek, openrouter, etc.).
        api_key: API key.
        model: Specific model (optional).
        context: Project context from CodeGraph.
    
    Returns:
        List of issues with improved accuracy.
    """
    # Validate provider name (prevent IDOR)
    VALID_PROVIDERS = {"ollama", "deepseek", "openrouter", "groq", "kimi", "qwen"}
    if provider not in VALID_PROVIDERS:
        raise ValueError(f"Invalid provider: {provider}. Must be one of: {', '.join(VALID_PROVIDERS)}")
    
    if not CLOUD_AVAILABLE:
        return fast_analyze(file_path, content)
    
    try:
        client = CloudClient(provider, api_key, model)
        
        # Get preliminary issues
        initial_issues = fast_analyze(file_path, content)
        
        # Format enhanced prompt
        prompt = _format_prompt(file_path, content, initial_issues, context)
        
        response = client.chat(prompt)
        
        # Parse JSON from response
        issues: List[Dict[str, Any]] = []
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                ai_data = json.loads(json_str)
                issues = _process_ai_results(file_path, ai_data, initial_issues)
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


def _process_ai_results(
    file_path: Path,
    ai_result: Dict[str, Any],
    initial_issues: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Process AI results, filter false positives, merge findings.
    
    This is the key improvement: AI reviews static analysis findings
    and removes false positives while adding new issues.
    """
    issues: List[Dict[str, Any]] = []
    
    # Get AI's false positive list
    false_positives = ai_result.get("false_positives", [])
    fp_set = {(fp.get("original_type"), fp.get("line")) for fp in false_positives}
    
    # Filter out false positives from initial issues
    for issue in initial_issues:
        loc = issue.get("location", "")
        line_num = int(loc.split(":")[-1]) if ":" in loc else 0
        issue_type = issue.get("type", "")
        
        if (issue_type, line_num) in fp_set:
            continue  # Skip false positive
        
        issues.append(issue)
    
    # Add AI-detected issues
    for ai_issue in ai_result.get("issues", []):
        line = ai_issue.get("line", 0)
        issues.append({
            "severity": ai_issue.get("severity", "warning"),
            "type": ai_issue.get("type", "ai-detected"),
            "location": f"{file_path.name}:{line}" if line else file_path.name,
            "message": ai_issue.get("message", "Issue detected"),
            "evidence": ai_issue.get("evidence", ""),
            "recommendation": ai_issue.get("recommendation", ""),
            "cwe": ai_issue.get("cwe", ""),
            "source": "ai",
        })
    
    # Deduplicate by location + type
    seen = set()
    unique_issues = []
    for issue in issues:
        key = (issue["location"], issue["type"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)
    
    return unique_issues


def analyze_with_context(
    root_path: Path,
    file_path: Path,
    content: str,
    mode: str = "fast",
) -> List[Dict[str, Any]]:
    """Full context-aware analysis.
    
    This is the presubmit-level feature: analyzes file with knowledge
    of the entire project structure and data flows.
    
    Args:
        root_path: Project root directory.
        file_path: File to analyze.
        content: File contents.
        mode: Analysis mode (fast, ai, cloud).
    
    Returns:
        List of issues with cross-file context.
    """
    # Build or load project graph
    cache_path = root_path / ".ai-reviewer-graph.json"
    
    if cache_path.exists():
        graph = CodeGraph.load(cache_path)
    else:
        graph = CodeGraph(root_path)
        graph.scan_project()
        graph.save(cache_path)
    
    # Get context for this file
    rel_path = str(file_path.relative_to(root_path))
    context = graph.get_context_for_file(rel_path)
    
    # Run analysis with context
    if mode == "fast":
        return fast_analyze(file_path, content)
    elif mode == "ai":
        return ai_analyze(file_path, content, context)
    else:
        # Cloud mode requires API key, handled separately
        return fast_analyze(file_path, content)
