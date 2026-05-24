"""Report generators for ai-reviewer"""
import json
import time
from typing import Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def print_rich_results(results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Print results to terminal with Rich formatting."""
    critical_count = len(results.get("critical", []))
    warning_count = len(results.get("warning", []))
    info_count = len(results.get("info", []))
    has_issues = (critical_count + warning_count + info_count) > 0

    if critical_count:
        console.print(f"\n[bold red]⚠️  CRITICAL ({critical_count})[/bold red]")
        table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
        table.add_column("Severity", style="red", width=10)
        table.add_column("Type", style="red", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["critical"]:
            msg = issue.get("message", "")
            rec = issue.get("recommendation", "")
            if rec:
                msg = f"{msg}\n[dim]→ {rec}[/dim]"
            table.add_row("CRITICAL", issue["type"], issue["location"], msg)
        console.print(table)
    
    if warning_count:
        console.print(f"\n[bold yellow]🔶 WARNING ({warning_count})[/bold yellow]")
        table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
        table.add_column("Severity", style="yellow", width=10)
        table.add_column("Type", style="yellow", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["warning"]:
            msg = issue.get("message", "")
            rec = issue.get("recommendation", "")
            if rec:
                msg = f"{msg}\n[dim]→ {rec}[/dim]"
            table.add_row("WARNING", issue["type"], issue["location"], msg)
        console.print(table)
    
    if info_count:
        console.print(f"\n[bold blue]💡 INFO ({info_count})[/bold blue]")
        table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
        table.add_column("Severity", style="blue", width=10)
        table.add_column("Type", style="blue", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["info"]:
            msg = issue.get("message", "")
            rec = issue.get("recommendation", "")
            if rec:
                msg = f"{msg}\n[dim]→ {rec}[/dim]"
            table.add_row("INFO", issue["type"], issue["location"], msg)
        console.print(table)
    
    if not has_issues:
        console.print("\n[bold green]✅ Clean! No issues found.[/bold green]")


def save_json_report(
    results: Dict[str, List[Dict[str, Any]]],
    output_path: str,
) -> None:
    """Save report as JSON."""
    # Validate output_path to prevent directory traversal
    if ".." in output_path:
        raise ValueError("Invalid output path: directory traversal detected")
    
    report = {
        "version": "1.2",
        "tool": "ai-reviewer",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "critical": len(results["critical"]),
            "warning": len(results["warning"]),
            "info": len(results["info"]),
        },
        "issues": [],
    }
    
    for severity in ("critical", "warning", "info"):
        for issue in results[severity]:
            report["issues"].append({
                "severity": severity,
                **issue,
            })
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def save_html_report(
    results: Dict[str, List[Dict[str, Any]]],
    output_path: str,
) -> None:
    """Save report as HTML."""
    # Validate output_path to prevent directory traversal
    if ".." in output_path:
        raise ValueError("Invalid output path: directory traversal detected")

    critical_count = len(results.get("critical", []))
    warning_count = len(results.get("warning", []))
    info_count = len(results.get("info", []))

    html = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "    <meta charset=\"utf-8\">\n"
        "    <title>ai-reviewer Report</title>\n"
        "    <style>\n"
        "        body {\n"
        "            font-family: 'Segoe UI', Arial, sans-serif;\n"
        "            margin: 40px;\n"
        "            background: #0f0f1a;\n"
        "            color: #e0e0e0;\n"
        "        }\n"
        "        h1 { color: #e94560; }\n"
        "        h2 { color: #4ecca3; }\n"
        "        .critical {\n"
        "            background: #3a1010;\n"
        "            padding: 12px;\n"
        "            margin: 6px 0;\n"
        "            border-left: 4px solid #e94560;\n"
        "            border-radius: 4px;\n"
        "        }\n"
        "        .warning {\n"
        "            background: #3a3010;\n"
        "            padding: 12px;\n"
        "            margin: 6px 0;\n"
        "            border-left: 4px solid #f4a261;\n"
        "            border-radius: 4px;\n"
        "        }\n"
        "        .info {\n"
        "            background: #10303a;\n"
        "            padding: 12px;\n"
        "            margin: 6px 0;\n"
        "            border-left: 4px solid #2a9d8f;\n"
        "            border-radius: 4px;\n"
        "        }\n"
        "        .location {\n"
        "            font-family: 'Fira Code', monospace;\n"
        "            color: #4ecca3;\n"
        "            font-size: 0.9em;\n"
        "        }\n"
        "        .message { margin-top: 4px; }\n"
        "        .summary {\n"
        "            background: #1a1a2e;\n"
        "            padding: 20px;\n"
        "            border-radius: 8px;\n"
        "            margin-bottom: 20px;\n"
        "        }\n"
        "    </style>\n"
        "</head>\n"
        "<body>\n"
        f"    <h1>🤖 ai-reviewer Report</h1>\n"
        f"    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
        "    <div class=\"summary\">\n"
        "        <h2>Summary</h2>\n"
        f"        <p><strong>Critical:</strong> {critical_count}</p>\n"
        f"        <p><strong>Warning:</strong> {warning_count}</p>\n"
        f"        <p><strong>Info:</strong> {info_count}</p>\n"
        "    </div>\n"
    )
    
    if results["critical"]:
        html += "<h2>Critical Issues</h2>\n"
        for issue in results["critical"]:
            html += f"""<div class="critical">
                <span class="location">{issue['location']}</span>
                <div class="message">{issue['message']}</div>
            </div>\n"""
    
    if results["warning"]:
        html += "<h2>Warnings</h2>\n"
        for issue in results["warning"]:
            html += f"""<div class="warning">
                <span class="location">{issue['location']}</span>
                <div class="message">{issue['message']}</div>
            </div>\n"""
    
    if results["info"]:
        html += "<h2>Suggestions</h2>\n"
        for issue in results["info"]:
            html += f"""<div class="info">
                <span class="location">{issue['location']}</span>
                <div class="message">{issue['message']}</div>
            </div>\n"""
    
    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def save_sarif_report(
    results: Dict[str, List[Dict[str, Any]]],
    output_path: str,
) -> None:
    """Save report in SARIF format for GitHub Code Scanning."""
    # Validate output_path to prevent directory traversal
    if ".." in output_path:
        raise ValueError("Invalid output path: directory traversal detected")
    
    # Map our severity to SARIF levels
    severity_map = {
        "critical": "error",
        "warning": "warning",
        "info": "note"
    }
    
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "ai-reviewer",
                    "version": "1.2",
                    "informationUri": "https://github.com/briej/ai-reviewer",
                }
            },
            "results": [],
        }]
    }
    
    for severity in ("critical", "warning", "info"):
        sarif_level = severity_map[severity]
        for issue in results[severity]:
            # Clean location for SARIF (remove line number for root level)
            location = issue["location"]
            if ":" in location:
                location = location.split(":")[0]
            
            sarif["runs"][0]["results"].append({
                "message": {"text": issue["message"]},
                "level": sarif_level,
                "ruleId": issue["type"],
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": location},
                    }
                }],
            })
    
    import json

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2)
