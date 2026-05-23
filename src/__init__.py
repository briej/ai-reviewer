"""ai-reviewer source package"""

__version__ = "1.2.0"

from .config import load_config
from .scanner import scan_files, read_file
from .analyzer import fast_analyze
from .ai_analyzer import ai_analyze, cloud_analyze
from .reporter import (
    print_rich_results,
    save_json_report,
    save_html_report,
    save_sarif_report,
)

__all__ = [
    "load_config",
    "scan_files",
    "read_file",
    "fast_analyze",
    "ai_analyze",
    "cloud_analyze",
    "print_rich_results",
    "save_json_report",
    "save_html_report",
    "save_sarif_report",
]
