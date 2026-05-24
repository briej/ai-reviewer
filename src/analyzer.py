"""Static analysis engine for ai-reviewer"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any


# Cache for loaded rules
_RULES_CACHE: Dict[str, Any] = None
_PYTHON_NESTING_KEYWORDS = (
    "if ", "elif ", "else:", "for ", "while ", "try:", "except ", "finally:",
    "with ", "async with ", "match ", "case "
)


def _load_rules() -> Dict[str, Any]:
    """Load rules from config/rules.json with caching."""
    global _RULES_CACHE
    if _RULES_CACHE is not None:
        return _RULES_CACHE
    
    rules_path = Path(__file__).parent.parent / "config" / "rules.json"
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            _RULES_CACHE = json.load(f)
    except (OSError, json.JSONDecodeError):
        _RULES_CACHE = {}
    return _RULES_CACHE


def _get_lang(file_path: Path) -> str:
    """Map file extension to language name."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".sql": "sql",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }
    return ext_map.get(file_path.suffix.lower(), "")


def _apply_metric_rules(
    file_path: Path,
    lines: List[str],
    lang: str,
    rules: Dict[str, Any],
    issues: List[Dict[str, Any]],
) -> None:
    """Apply metric-based rules (line count, nesting depth, etc.)."""
    file_name = file_path.name
    
    for category, cat_rules in rules.items():
        for rule_id, rule in cat_rules.items():
            if rule.get("type") != "metric":
                continue
            if lang not in rule.get("languages", []):
                continue
            
            metric = rule.get("metric")
            threshold = rule.get("threshold", 0)
            
            if metric == "line_count":
                # Check each function length
                in_func = False
                func_start = 0
                indent_level = 0
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("def ") or stripped.startswith("function "):
                        in_func = True
                        func_start = i
                        indent_level = len(line) - len(line.lstrip())
                    elif in_func and stripped:
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent <= indent_level and not stripped.startswith("#"):
                            func_lines = i - func_start
                            if func_lines > threshold:
                                issues.append({
                                    "severity": rule.get("severity", "warning"),
                                    "type": rule_id,
                                    "location": f"{file_name}:{func_start}",
                                    "message": rule.get("message", "Metric issue"),
                                })
                            in_func = False
                # Check last function
                if in_func:
                    func_lines = len(lines) - func_start + 1
                    if func_lines > threshold:
                        issues.append({
                            "severity": rule.get("severity", "warning"),
                            "type": rule_id,
                            "location": f"{file_name}:{func_start}",
                            "message": rule.get("message", "Metric issue"),
                        })
            
            elif metric == "nesting_depth":
                max_depth, max_line = _max_nesting_depth(lines, lang)
                if max_depth > threshold:
                    issues.append({
                        "severity": rule.get("severity", "warning"),
                        "type": rule_id,
                        "location": f"{file_name}:{max_line}",
                        "message": rule.get("message", "Deep nesting"),
                    })
            
            elif metric == "arg_count":
                for i, line in enumerate(lines, 1):
                    match = re.search(r"def\s+\w+\s*\((.*?)\)", line)
                    if match:
                        args = match.group(1)
                        # Count non-empty args
                        arg_count = len([a.strip() for a in args.split(",") if a.strip() and a.strip() != "self" and a.strip() != "cls"])
                        if arg_count > threshold:
                            issues.append({
                                "severity": rule.get("severity", "info"),
                                "type": rule_id,
                                "location": f"{file_name}:{i}",
                                "message": rule.get("message", "Too many args"),
                            })


def _max_nesting_depth(lines: List[str], lang: str) -> tuple[int, int]:
    """Calculate approximate control-flow nesting depth for Python/JS-like files."""
    if lang == "python":
        return _max_python_nesting_depth(lines)
    if lang in ("javascript", "typescript"):
        return _max_brace_nesting_depth(lines)
    return 0, 0


def _max_python_nesting_depth(lines: List[str]) -> tuple[int, int]:
    max_depth = 0
    max_line = 0
    stack: List[int] = []

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        while stack and indent <= stack[-1]:
            stack.pop()

        if stripped.endswith(":") and stripped.startswith(_PYTHON_NESTING_KEYWORDS):
            stack.append(indent)
            if len(stack) > max_depth:
                max_depth = len(stack)
                max_line = line_number

    return max_depth, max_line


def _max_brace_nesting_depth(lines: List[str]) -> tuple[int, int]:
    max_depth = 0
    max_line = 0
    depth = 0

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue

        depth = max(0, depth - stripped.count("}"))
        depth += stripped.count("{")
        if depth > max_depth:
            max_depth = depth
            max_line = line_number

    return max_depth, max_line


def _is_empty_html_assignment(line: str) -> bool:
    match = re.search(r"\.(?:innerHTML|outerHTML)\s*=\s*([^;]+)", line)
    if not match:
        return False
    return match.group(1).strip() in ("''", '""', "``")


def fast_analyze(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Fast rule-based analysis (OWASP Top 10 + custom rules from JSON).
    
    Args:
        file_path: Path to the file being analyzed.
        content: File contents.
    
    Returns:
        List of issues found.
    """
    issues: List[Dict[str, Any]] = []
    lines = content.split("\n")
    lang = _get_lang(file_path)
    
    # Load rules from JSON
    rules = _load_rules()
    
    # Apply pattern-based rules from JSON
    if rules:
        for category, cat_rules in rules.items():
            for rule_id, rule in cat_rules.items():
                # Skip metric rules (handled separately)
                if rule.get("type") == "metric":
                    continue
                
                # Check language filter
                rule_langs = rule.get("languages", [])
                if rule_langs and lang not in rule_langs:
                    continue
                
                pattern = rule.get("pattern", "")
                if not pattern:
                    continue
                
                for i, line in enumerate(lines, 1):
                    try:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                "severity": rule.get("severity", "warning"),
                                "type": rule_id,
                                "location": f"{file_path.name}:{i}",
                                "message": rule.get("message", f"Issue detected by {rule_id}"),
                            })
                    except re.error:
                        # Skip invalid regex patterns
                        continue
    
    # Apply metric-based rules
    _apply_metric_rules(file_path, lines, lang, rules, issues)
    
    # Built-in hardcoded rules (backward compatibility + JS-specific)
    for i, line in enumerate(lines, 1):
        # Weak hashes
        if re.search(r"\b(md5|sha1)\s*\(", line, re.IGNORECASE):
            if not any(i["type"] == "weak-crypto" for i in issues if i["location"] == f"{file_path.name}:{i}"):
                issues.append({
                    "severity": "warning",
                    "type": "weak-crypto",
                    "location": f"{file_path.name}:{i}",
                    "message": "Weak hash. Use SHA-256, bcrypt, or Argon2.",
                })
            
        # JavaScript / TypeScript specific
        if lang in ("javascript", "typescript"):
            if ("innerHTML" in line or "outerHTML" in line) and not _is_empty_html_assignment(line):
                if not any(i["type"] == "xss" and "innerHTML" in i["message"] for i in issues):
                    issues.append({
                        "severity": "warning",
                        "type": "xss",
                        "location": f"{file_path.name}:{i}",
                        "message": "innerHTML is vulnerable to XSS. Use textContent.",
                    })
            
            if "document.write" in line:
                issues.append({
                    "severity": "critical",
                    "type": "xss",
                    "location": f"{file_path.name}:{i}",
                    "message": "document.write is deprecated and dangerous.",
                })
            
            if "console.log" in line or "console.error" in line:
                issues.append({
                    "severity": "info",
                    "type": "debug",
                    "location": f"{file_path.name}:{i}",
                    "message": "console.log found — remove before production.",
                })
        
    # OWASP A05: Security Misconfiguration
    if re.search(r"\bDEBUG\s*=\s*True\b|\bdebug\s*=\s*True\b", content):
        if not any(i["type"] == "debug-enabled" for i in issues):
            issues.append({
                "severity": "critical",
                "type": "debug-enabled",
                "location": file_path.name,
                "message": "DEBUG mode enabled — disable in production.",
            })
    
    # Deduplicate issues by location + type
    seen = set()
    unique_issues = []
    for issue in issues:
        key = (issue["location"], issue["type"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)
    
    return unique_issues
