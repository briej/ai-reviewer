"""Report generators for ai-reviewer"""
import json
import time
from typing import Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def print_rich_results(results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Print results to terminal with Rich formatting."""
    if results["critical"]:
        console.print(f"\n[bold red]⚠️  CRITICAL ({len(results['critical'])})[/bold red]")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Type", style="red", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["critical"]:
            table.add_row(issue["type"], issue["location"], issue["message"])
        console.print(table)
    
    if results["warning"]:
        console.print(f"\n[bold yellow]🔶 WARNING ({len(results['warning'])})[/bold yellow]")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Type", style="yellow", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["warning"]:
            table.add_row(issue["type"], issue["location"], issue["message"])
        console.print(table)
    
    if results["info"]:
        console.print(f"\n[bold blue]💡 INFO ({len(results['info'])})[/bold blue]")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Type", style="blue", width=20)
        table.add_column("Location", style="dim cyan")
        table.add_column("Message", style="white")
        for issue in results["info"]:
            table.add_row(issue["type"], issue["location"], issue["message"])
        console.print(table)
    
    if not any(results.values()):
        console.print("\n[bold green]✅ Clean! No issues found.[/bold green]")


def save_json_report(results: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save report as JSON."""
    # Validate output_path to prevent directory traversal
    if ".." in output_path:
        raise ValueError(f"Invalid output path: {output_path}. Directory traversal detected.")
    
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


def save_html_report(results: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save report as HTML."""
    # Validate output_path to prevent directory traversal
    output_path_obj = Path(output_path)
    if ".." in str(output_path):
        raise ValueError(f"Invalid output path: {output_path}. Directory traversal detected.")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ai-reviewer Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #0f0f1a; color: #e0e0e0; }}
        h1 {{ color: #e94560; }}
        h2 {{ color: #4ecca3; }}
        .critical {{ background: #3a1010; padding: 12px; margin: 6px 0; border-left: 4px solid #e94560; border-radius: 4px; }}
        .warning {{ background: #3a3010; padding: 12px; margin: 6px 0; border-left: 4px solid #f4a261; border-radius: 4px; }}
        .info {{ background: #10303a; padding: 12px; margin: 6px 0; border-left: 4px solid #2a9d8f; border-radius: 4px; }}
        .location {{ font-family: 'Fira Code', monospace; color: #4ecca3; font-size: 0.9em; }}
        .message {{ margin-top: 4px; }}
        .summary {{ background: #1a1a2e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>🤖 ai-reviewer Report</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Critical:</strong> {len(results['critical'])}</p>
        <p><strong>Warning:</strong> {len(results['warning'])}</p>
        <p><strong>Info:</strong> {len(results['info'])}</p>
    </div>
"""
    
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


def save_sarif_report(results: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save report in SARIF format for GitHub Code Scanning."""
    # Validate output_path to prevent directory traversal
    if ".." in output_path:
        raise ValueError(f"Invalid output path: {output_path}. Directory traversal detected.")
    
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
