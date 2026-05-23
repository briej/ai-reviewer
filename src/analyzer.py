"""Static analysis engine for ai-reviewer"""
import re
from pathlib import Path
from typing import List, Dict, Any


def fast_analyze(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Fast rule-based analysis (OWASP Top 10).
    
    Args:
        file_path: Path to the file being analyzed.
        content: File contents.
    
    Returns:
        List of issues found.
    """
    issues: List[Dict[str, Any]] = []
    lines = content.split("\n")
    lang = file_path.suffix.lower()
    
    # OWASP A02: Cryptographic Failures
    for i, line in enumerate(lines, 1):
        # Hardcoded secrets
        if re.search(
            r"(password|passwd|pwd|secret|api_key|apikey|token)\s*=\s*['\"][^'\"]{4,}['\"]",
            line, re.IGNORECASE,
        ):
            issues.append({
                "severity": "critical",
                "type": "hardcoded-secret",
                "location": f"{file_path.name}:{i}",
                "message": "Hardcoded secret. Use environment variables.",
            })
        
        # Hardcoded API keys
        if re.search(
            r"(api[_-]?key|apikey|access[_-]?token)\s*=\s*['\"][a-zA-Z0-9]{16,}['\"]",
            line, re.IGNORECASE,
        ):
            issues.append({
                "severity": "critical",
                "type": "hardcoded-api-key",
                "location": f"{file_path.name}:{i}",
                "message": "Hardcoded API key. Use os.getenv() or dotenv.",
            })
        
        # Weak hashes
        if re.search(r"\b(md5|sha1)\s*\(", line, re.IGNORECASE):
            issues.append({
                "severity": "warning",
                "type": "weak-crypto",
                "location": f"{file_path.name}:{i}",
                "message": "Weak hash. Use SHA-256, bcrypt, or Argon2.",
            })
        
        # SQL Injection
        if re.search(r"execute\s*\(\s*f?['\"].*\{.*\}", line, re.IGNORECASE):
            issues.append({
                "severity": "critical",
                "type": "sql-injection",
                "location": f"{file_path.name}:{i}",
                "message": "SQL Injection via f-string. Use parameterized queries.",
            })
        
        # eval / exec
        if re.search(r"\b(eval|exec)\s*\(", line):
            issues.append({
                "severity": "critical",
                "type": "code-injection",
                "location": f"{file_path.name}:{i}",
                "message": "eval()/exec() are dangerous — possible RCE.",
            })
        
        # JavaScript / TypeScript specific
        if lang in (".js", ".ts", ".jsx", ".tsx"):
            if "innerHTML" in line or "outerHTML" in line:
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
            
            if "eval(" in line:
                issues.append({
                    "severity": "critical",
                    "type": "code-injection",
                    "location": f"{file_path.name}:{i}",
                    "message": "eval() is dangerous for XSS.",
                })
            
            if "console.log" in line or "console.error" in line:
                issues.append({
                    "severity": "info",
                    "type": "debug",
                    "location": f"{file_path.name}:{i}",
                    "message": "console.log found — remove before production.",
                })
        
        # Insecure random
        if re.search(r"\brandom\.(random|randint)\b", line):
            issues.append({
                "severity": "warning",
                "type": "insecure-random",
                "location": f"{file_path.name}:{i}",
                "message": "random is not cryptographically secure. Use secrets.",
            })
        
        # Bare except
        if re.match(r"\s*except\s*:", line):
            issues.append({
                "severity": "warning",
                "type": "bare-except",
                "location": f"{file_path.name}:{i}",
                "message": "Bare except catches everything — be specific.",
            })
        
        # Mutable default arguments
        if re.search(r"def\s+\w+\s*\([^)]*=\[\]|def\s+\w+\s*\([^)]*=\{\}", line):
            issues.append({
                "severity": "warning",
                "type": "mutable-default",
                "location": f"{file_path.name}:{i}",
                "message": "Mutable default argument — anti-pattern.",
            })
    
    # OWASP A05: Security Misconfiguration
    if "DEBUG = True" in content or "debug=True" in content:
        issues.append({
            "severity": "critical",
            "type": "debug-enabled",
            "location": file_path.name,
            "message": "DEBUG mode enabled — disable in production.",
        })
    
    return issues
