#!/usr/bin/env python3
"""ai-reviewer CLI — v1.4

AI-powered code reviewer with OWASP Top 10 checks.
Fast. Local. Configurable. Context-aware.
"""

import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from src.scanner import scan_files, read_file
from src.analyzer import fast_analyze
from src.context_analyzer import CodeGraph
from src.ai_analyzer import ai_analyze, cloud_analyze
from src.reporter import (
    print_rich_results,
    save_json_report,
    save_html_report,
    save_sarif_report,
)

console = Console()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROVIDER_CHOICES = ("ollama", "openrouter", "deepseek", "kimi", "qwen", "groq")


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--mode", "-m", default="fast",
              type=click.Choice(["fast", "ai", "cloud", "context"]),
              help="Mode: fast (rules), ai (Ollama), cloud (API), context (cross-file)")


@click.option("--provider", "-p",
              type=click.Choice(PROVIDER_CHOICES),
              help="AI provider (for ai/cloud mode)")
@click.option("--api-key", "-k", help="API key (for cloud mode)")
@click.option("--model", "--model-name", "-M",
              help="AI model (e.g., llama3.2, deepseek-coder)")
@click.option("--output", "-o", type=click.Path(), help="Report file path")
@click.option("--format", "-f", "output_format",
              type=click.Choice(["cli", "json", "html", "sarif"]),
              default="cli", help="Output format")
@click.option("--severity", "-s",
              type=click.Choice(["critical", "warning", "info", "all"]),
              default="all", help="Minimum severity to report")
@click.option("--threads", "-t", type=int, default=4,
              help="Number of parallel threads")
@click.option("--ignore", "-i", multiple=True,
              help="Ignore patterns (e.g., __pycache__, .git)")
@click.option("--verbose", "-v", is_flag=True,
              help="Show detailed progress")
@click.option("--cache-graph", is_flag=True,
              help="Cache project graph for faster subsequent runs")
@click.option("--no-context", is_flag=True,
              help="Disable context-aware analysis")
@click.version_option(version="1.4.0", prog_name="ai-review")
def main(path, mode, provider, api_key, model, output, output_format,
         severity, threads, ignore, verbose, cache_graph, no_context):
    """ai-reviewer — code review with OWASP Top 10 checks and context awareness.

    \b
    Examples:
      ai-review ./project --mode fast
      ai-review ./project --mode ai --provider ollama --model llama3.2
      ai-review ./project --mode cloud --provider deepseek --api-key sk-xxx
      ai-review ./project --mode context --cache-graph
      ai-review ./project --format html --output report.html
      ai-review ./project --threads 8 --verbose
    """
    console.print(Panel.fit(
        "[bold cyan]🤖 ai-reviewer — v1.4[/bold cyan]\n"
        "[dim]OWASP Top 10 | Context-Aware | Multi-Cloud | Local AI | Parallel[/dim]",
        border_style="cyan",
    ))

    # Validate cloud mode
    if mode in ("ai", "cloud"):
        if not provider:
            provider = "ollama"  # Default to Ollama for ai mode
        if mode == "cloud" and not api_key:
            console.print(f"[red]Error:[/red] --api-key required for {mode} mode")
            sys.exit(1)

    # Context mode implies ai mode
    if mode == "context":
        no_context = False

    # Scan files
    start_time = time.time()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Scanning files...", total=None)
        files = scan_files(path, ignore_patterns=ignore)

    console.print(f"[green]✓[/green] Files found: [bold]{len(files)}[/bold]")

    # Build context graph if using context mode
    context_graph = None
    if mode == "context" and not no_context:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("[cyan]Building project context...", total=None)
            context_graph = CodeGraph(Path(path))
            context_graph.scan_project()
            if cache_graph:
                cache_path = Path(path) / ".ai-reviewer-graph.json"
                context_graph.save(cache_path)
                console.print(f"[dim]Graph cached at {cache_path}[/dim]")

    # Analyze
    results = {"critical": [], "warning": [], "info": []}
    analyzed = 0

    # Single-threaded or AI mode
    for fp in files:
        content = read_file(fp)
        if content is None:
            continue

        try:
            if mode == "fast":
                issues = fast_analyze(fp, content)
            elif mode == "context" and context_graph:
                # Context-aware analysis
                rel_path = str(fp.relative_to(Path(path)))
                file_context = context_graph.get_context_for_file(rel_path)
                issues = ai_analyze(fp, content, file_context)
            elif mode == "ai":
                # AI mode without full context (faster)
                issues = ai_analyze(fp, content)
            else:
                # Cloud mode
                issues = cloud_analyze(
                    fp, content,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                )
            
            for issue in issues:
                results[issue["severity"]].append(issue)
            analyzed += 1
            if verbose:
                console.print(f"  [green]✓[/green] {fp.name}")
                    
        except Exception as e:
            if verbose:
                console.print(f"  [red]✗[/red] {fp.name}: {e}")
            continue

    elapsed = time.time() - start_time

    # Filter severity
    if severity != "all":
        order = ["critical", "warning", "info"]
        idx = order.index(severity)
        filtered = {k: results[k] for k in order[idx:]}
        results = filtered

    # Output
    if output_format == "json":
        save_json_report(results, output or "report.json")
    elif output_format == "html":
        save_html_report(results, output or "report.html")
    elif output_format == "sarif":
        save_sarif_report(results, output or "report.sarif")
    else:
        print_rich_results(results)

    # Summary
    console.print()
    console.print("─" * 50)

    stats = Table(box=box.ROUNDED, show_header=False, border_style="dim")
    stats.add_column("Metric", style="cyan")
    stats.add_column("Value", style="bold")
    stats.add_row("Files analyzed", f"{analyzed}/{len(files)}")
    stats.add_row("Time", f"{elapsed:.2f}s")
    crit_count = len(results.get("critical", []))
    warn_count = len(results.get("warning", []))
    info_count = len(results.get("info", []))

    stats.add_row("Critical", f"[red]{crit_count}[/red]")
    stats.add_row("Warning", f"[yellow]{warn_count}[/yellow]")
    stats.add_row("Info", f"[blue]{info_count}[/blue]")

    score = max(0, round(10.0 - crit_count * 1.5 - warn_count * 0.5, 1))
    color = "green" if score >= 8 else "yellow" if score >= 5 else "red"
    stats.add_row("Score", f"[{color}]{score}/10[/{color}]")
    console.print(stats)

    # Exit codes for CI/CD
    if results["critical"]:
        sys.exit(2)
    elif results["warning"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
