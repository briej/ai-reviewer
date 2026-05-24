#!/usr/bin/env python3
"""ai-reviewer CLI — v1.2

AI-powered code reviewer with OWASP Top 10 checks.
Fast. Local. Configurable.
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from src.scanner import scan_files, read_file
from src.analyzer import fast_analyze
from src.cloud_client import analyze_with_ai, AIError
from src.reporter import (
    print_rich_results,
    save_json_report,
    save_html_report,
    save_sarif_report,
)

console = Console()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--mode", "-m", default="fast",
              type=click.Choice(["fast", "ai", "cloud"]),
              help="Mode: fast (rules), ai (Ollama), cloud (API)")
@click.option("--provider", "-p",
              type=click.Choice(["ollama", "openrouter", "deepseek", "kimi", "qwen", "groq"]),
              help="AI provider (for ai/cloud mode)")
@click.option("--api-key", "-k", help="API key (for cloud mode)")
@click.option("--model", "--model-name", "-M",
              help="AI model (e.g., llama3.1, deepseek-coder)")
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
@click.version_option(version="1.3.0", prog_name="ai-review")
def main(path, mode, provider, api_key, model, output, output_format,
         severity, threads, ignore, verbose):
    """ai-reviewer — code review with OWASP Top 10 checks.

    \b
    Examples:
      ai-review ./project --mode fast
      ai-review ./project --mode ai --provider ollama --model llama3.1
      ai-review ./project --mode cloud --provider deepseek --api-key sk-xxx
      ai-review ./project --format html --output report.html
      ai-review ./project --threads 8 --verbose
    """
    console.print(Panel.fit(
        "[bold cyan]🤖 ai-reviewer — v1.3[/bold cyan]\n"
        "[dim]OWASP Top 10 | AI-Powered | Multi-Cloud | Parallel | Rich CLI[/dim]",
        border_style="cyan",
    ))

    # Validate cloud mode
    if mode in ("ai", "cloud"):
        if not provider:
            provider = "ollama"  # Default to Ollama for ai mode
        if mode == "cloud" and not api_key:
            console.print(f"[red]Error:[/red] --api-key required for {mode} mode")
            sys.exit(1)

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

    # Analyze
    results = {"critical": [], "warning": [], "info": []}
    analyzed = 0

    if threads > 1 and mode == "fast":
        # Parallel mode (fast only)
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(fast_analyze, fp, read_file(fp) or ""): fp
                for fp in files
            }
            for future in as_completed(futures):
                fp = futures[future]
                try:
                    issues = future.result()
                    for issue in issues:
                        results[issue["severity"]].append(issue)
                    analyzed += 1
                    if verbose:
                        console.print(f"  [green]✓[/green] {fp.name}")
                except Exception as exc:
                    if verbose:
                        console.print(f"  [red]✗[/red] {fp.name}: {exc}")
    else:
        # Single-threaded or AI mode
        for fp in files:
            content = read_file(fp)
            if content is None:
                continue

            try:
                if mode == "fast":
                    issues = fast_analyze(fp, content)
                else:
                    # AI or cloud mode
                    initial_issues = fast_analyze(fp, content)
                    ai_results = analyze_with_ai(
                        fp, content, initial_issues,
                        provider=provider,
                        model=model,
                        api_key=api_key,
                    )
                    
                    # Convert AI results to issue format
                    issues = []
                    for ai_issue in ai_results.get("issues", []):
                        issues.append({
                            "severity": ai_issue.get("severity", "warning"),
                            "type": ai_issue.get("type", "ai-review"),
                            "location": f"{fp.name}:{ai_issue.get('line', 0)}",
                            "message": f"{ai_issue.get('message', '')} - {ai_issue.get('recommendation', '')}",
                        })
                    
                    if verbose and ai_results.get("false_positives"):
                        console.print(f"  [dim]AI removed {len(ai_results['false_positives'])} false positives[/dim]")
                
                for issue in issues:
                    results[issue["severity"]].append(issue)
                analyzed += 1
                if verbose:
                    console.print(f"  [green]✓[/green] {fp.name}")
                    
            except AIError as e:
                console.print(f"  [red]✗[/red] {fp.name}: {e}")
                continue
            except Exception as e:
                if verbose:
                    console.print(f"  [red]✗[/red] {fp.name}: {e}")

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
    stats.add_row("Critical", f"[red]{len(results['critical'])}[/red]")
    stats.add_row("Warning", f"[yellow]{len(results['warning'])}[/yellow]")
    stats.add_row("Info", f"[blue]{len(results['info'])}[/blue]")

    score = max(0, round(10.0 - len(results["critical"]) * 1.5 - len(results["warning"]) * 0.5, 1))
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
