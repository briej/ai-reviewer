"""File scanner for ai-reviewer"""
import fnmatch
from pathlib import Path
from typing import List, Set, Optional

from .config import load_config


def scan_files(path: str, ignore_patterns: Optional[Set[str]] = None) -> List[Path]:
    """Scan directory for code files.

    Args:
        path: Path to file or directory.
        ignore_patterns: Patterns to ignore (e.g., '__pycache__', '.git').

    Returns:
        Sorted list of file paths.
    """
    config = load_config()
    
    if not ignore_patterns:
        ignore_patterns = set(config.get("ignore", []))
    else:
        ignore_patterns = set(ignore_patterns)
    
    extensions = config.get("languages", {})
    # Support both formats: {".py": "python"} and {"python": [".py"]}
    ext_set = set()
    for key, value in extensions.items():
        if isinstance(value, list):
            ext_set.update(value)
        elif isinstance(value, str) and key.startswith("."):
            ext_set.add(key)
    
    path_obj = Path(path)
    if path_obj.is_file():
        return [path_obj] if path_obj.suffix.lower() in ext_set else []
    files: List[Path] = []
    for ext in ext_set:
        files.extend(path_obj.rglob(f"*{ext}"))
    # Filter ignored patterns
    filtered: List[Path] = []
    for f in files:
        if not _is_ignored(f, path_obj, ignore_patterns):
            filtered.append(f)
    return sorted(filtered)


def _is_ignored(file_path: Path, root_path: Path, ignore_patterns: Set[str]) -> bool:
    """Return True when a file matches an ignored path part or glob pattern."""
    try:
        base = root_path if root_path.is_dir() else root_path.parent
        relative_path = file_path.relative_to(base)
    except ValueError:
        relative_path = file_path

    normalized = relative_path.as_posix()
    for pattern in ignore_patterns:
        if not pattern:
            continue
        if pattern in file_path.parts:
            return True
        if fnmatch.fnmatch(file_path.name, pattern):
            return True
        if fnmatch.fnmatch(normalized, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in relative_path.parts):
            return True
    return False


def read_file(file_path: Path, max_size_mb: Optional[int] = None) -> Optional[str]:
    """Read file contents with size check.
    
    Args:
        file_path: Path to file.
        max_size_mb: Maximum file size in MB.
    
    Returns:
        File contents or None if too large/unreadable.
    """
    if max_size_mb is None:
        config = load_config()
        max_size_mb = config.get("max_file_size_mb", 10)
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return None
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (OSError, PermissionError, UnicodeDecodeError):
        return None
