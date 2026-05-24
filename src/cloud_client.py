"""AI-powered analysis using Ollama and other providers."""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # type: ignore


# AI Provider configurations
PROVIDERS = {
    "ollama": {
        "base_url": "http://localhost:11434",
        "default_model": "llama3.1",
        "chat_endpoint": "/api/generate",
        "stream": True,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-coder",
        "chat_endpoint": "/v1/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api",
        "default_model": "anthropic/claude-3.5-sonnet",
        "chat_endpoint": "/v1/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai",
        "default_model": "llama3-70b-8192",
        "chat_endpoint": "/v1/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
}


class AIError(Exception):
    """AI provider error."""
    pass


class CloudClient:
    """Client for cloud AI providers."""
    
    def __init__(self, provider: str, api_key: str, model: str = ""):
        if provider not in PROVIDERS:
            raise ValueError(f"Invalid provider: {provider}")
        self.provider = provider
        self.api_key = api_key
        self.model = model or PROVIDERS[provider]["default_model"]
        self.config = PROVIDERS[provider]
    
    def chat(self, prompt: str, timeout: int = 120) -> str:
        """Send chat request to cloud provider."""
        if requests is None:
            raise AIError("requests library not installed")
        
        url = f"{self.config['base_url']}{self.config['chat_endpoint']}"
        headers = {"Content-Type": "application/json"}

        # Add auth header only if provider requires it
        auth_header = self.config.get("auth_header")
        auth_prefix = self.config.get("auth_prefix", "")
        if auth_header:
            if not self.api_key:
                raise AIError(f"No API key provided for provider {self.provider}")
            headers[auth_header] = f"{auth_prefix}{self.api_key}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2048,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()

        result = response.json()

        # Return a string payload for downstream parsers. Support common shapes.
        if isinstance(result, dict):
            # OpenAI-like response
            try:
                return result["choices"][0]["message"]["content"]
            except Exception:
                # Ollama-like response
                if "response" in result:
                    return result.get("response", "")
                # Fallback: return serialized JSON
                return json.dumps(result)
        return str(result)


def _get_api_key(provider: str, api_key: Optional[str] = None) -> Optional[str]:
    """Get API key from parameter or environment variable."""
    if api_key:
        return api_key
    
    env_vars = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "groq": "GROQ_API_KEY",
        "kimi": "KIMI_API_KEY",
        "qwen": "QWEN_API_KEY",
    }
    
    env_var = env_vars.get(provider)
    if env_var:
        return os.getenv(env_var)
    
    return None


def _format_prompt(
    file_path: Path,
    content: str,
    issues: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """Format code and issues for AI analysis with context awareness."""
    lang = _detect_language(file_path)
    
    prompt = f"""# AI Code Review — Context-Aware Analysis

**File:** `{file_path.name}` ({file_path.suffix.lstrip('.') or 'unknown'})
**Lines:** {len(content.splitlines())}
**Context:** {context.get('project_type', 'unknown') if context else 'single file'}

---

## Code to Review

```{lang}
{content[:12000]}
```

---

## Static Analysis Findings (Preliminary)

"""
    
    if issues:
        prompt += "| Severity | Type | Location | Message |\n"
        prompt += "|----------|------|----------|---------|\n"
        for issue in issues[:15]:
            loc = issue.get('location', 'unknown')
            msg = issue.get('message', 'No message')[:80]
            sev = issue.get('severity', 'unknown')
            typ = issue.get('type', 'unknown')
            prompt += (
                "| {sev} | {typ} | {loc} | {msg} |\n".format(
                    sev=sev, typ=typ, loc=loc, msg=msg
                )
            )
    else:
        prompt += "*No issues detected by static analysis.*\n"
    
    # Add context about related files if available
    if context and context.get('related_files'):
        prompt += "\n## Related Files in Project\n"
        for rel_file in context['related_files'][:5]:
            prompt += f"- `{rel_file}`\n"
    
    prompt += """
---

## Analysis Task

Perform a **context-aware security and quality review**. Think step by step:

### Step 1: Understand the Code
- What is this file's purpose in the project?
- What are the security boundaries (user input, external APIs, etc.)?
- What data flows through this code?

### Step 2: Security Analysis (OWASP Top 10 Focus)
- **Injection**: SQL, NoSQL, OS command, LDAP, XPath
- **Authentication**: Session handling, token validation, password storage
- **Sensitive Data**: Encryption, secrets management, logging
- **XXE**: XML parsing with external entities
- **Broken Access Control**: Authorization checks, role-based access
- **Security Misconfiguration**: Debug modes, default credentials, verbose errors
- **Vulnerable Components**: Known CVEs in dependencies
- **Data Integrity**: Input validation, output encoding
- **Logging**: Security event logging, error handling

### Step 3: Quality & Best Practices
- Code readability and maintainability
- Error handling robustness
- Performance anti-patterns
- Testing coverage gaps

### Step 4: False Positive Detection
Review each static analysis finding:
- Is this actually a vulnerability in THIS context?
- Is the input properly validated/sanitized elsewhere?
- Is this a known safe pattern?

---

## Output Format (STRICT JSON ONLY)

Return **ONLY** a valid JSON object. No markdown, no explanations.

```json
{
  "review": {
    "summary": "One-sentence overall assessment",
    "risk_level": "low|medium|high|critical",
    "confidence": 0.0-1.0
  },
  "issues": [
    {
      "severity": "critical|warning|info",
      "type": "category-subcategory",
      "line": <line_number>,
      "end_line": <optional_end_line>,
      "message": "Clear, specific description",
      "evidence": "Code snippet or pattern that triggered this",
      "recommendation": "Actionable fix with code example",
      "cwe": "CWE-XXXX (optional)",
      "confidence": 0.0-1.0
    }
  ],
  "false_positives": [
    {
      "original_type": "type from static analysis",
      "line": <line_number>,
      "reason": "Why this is not actually a problem"
    }
  ],
  "suggestions": [
    "General improvement suggestion 1",
    "General improvement suggestion 2"
  ]
}
```

---

## Important Rules

1. **Be specific** — Don't say "possible injection".
    Example: "SQL injection at line 42: user input reaches execute()"
2. **Consider context** — If input is validated upstream, mark as false positive
3. **Prioritize** — Critical issues first, focus on real risks not style
4. **Be actionable** — Every issue must have a clear fix recommendation
5. **No hallucinations** — Only report what you see in the code

Respond with JSON ONLY.
"""
    
    return prompt


def _detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".sql": "sql",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
    }
    return ext_map.get(file_path.suffix.lower(), "text")


def analyze_with_ai(
    file_path: Path,
    content: str,
    initial_issues: List[Dict[str, Any]],
    provider: str = "ollama",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Analyze code with AI provider.
    
    Args:
        file_path: Path to the file.
        content: File contents.
        initial_issues: Issues from static analysis.
        provider: AI provider (ollama, deepseek, openrouter, groq).
        model: Model name (uses default if None).
        api_key: API key (for cloud providers).
        timeout: Request timeout in seconds.
    
    Returns:
        AI analysis results.
    """
    if provider not in PROVIDERS:
        raise AIError(f"Unknown provider: {provider}")
    
    config = PROVIDERS[provider]
    model = model or config["default_model"]
    
    prompt = _format_prompt(file_path, content, initial_issues)
    
    if provider == "ollama":
        return _ollama_request(prompt, model, timeout)
    else:
        return _cloud_request(provider, prompt, model, api_key, timeout)


def _ollama_request(prompt: str, model: str, timeout: int) -> Dict[str, Any]:
    """Send request to Ollama."""
    if requests is None:
        msg = "requests library not installed."
        msg += " Install with: pip install requests"
        raise AIError(msg)
    
    url = f"{PROVIDERS['ollama']['base_url']}{PROVIDERS['ollama']['chat_endpoint']}"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2048,
        },
    }
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        raw_text = result.get("response", "")
        
        # Parse JSON from response
        try:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(raw_text)
        except (json.JSONDecodeError, re.error):
            return {
                "issues": [],
                "false_positives": [],
                "summary": f"Failed to parse AI response: {raw_text[:200]}",
            }
    
    except requests.exceptions.ConnectionError:
        msg = "Cannot connect to Ollama."
        msg += " Make sure it's running on localhost:11434"
        raise AIError(msg)
    except requests.exceptions.Timeout:
        raise AIError(f"Request timed out after {timeout}s")
    except Exception as e:
        raise AIError(f"Ollama error: {str(e)}")


def _cloud_request(
    provider: str,
    prompt: str,
    model: str,
    api_key: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    """Send request to cloud AI provider."""
    if requests is None:
        msg = "requests library not installed."
        msg += " Install with: pip install requests"
        raise AIError(msg)
    
    config = PROVIDERS[provider]
    api_key = _get_api_key(provider, api_key)
    
    if not api_key:
        msg = f"No API key for {provider}."
        msg += f" Set {provider.upper()}_API_KEY or pass --api-key"
        raise AIError(msg)
    
    url = f"{config['base_url']}{config['chat_endpoint']}"
    
    headers = {"Content-Type": "application/json"}
    auth_hdr = config.get("auth_header")
    if auth_hdr:
        headers[auth_hdr] = f"{config.get('auth_prefix', '')}{api_key}"
    
    # Add OpenRouter-specific headers
    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/briej/ai-reviewer"
        headers["X-Title"] = "ai-reviewer"
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON from response
        try:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(content)
        except (json.JSONDecodeError, re.error):
            return {
                "issues": [],
                "false_positives": [],
                "summary": f"Failed to parse AI response: {content[:200]}",
            }
    
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.text if e.response else str(e)
        raise AIError(f"{provider} API error: {error_msg}")
    except requests.exceptions.Timeout:
        raise AIError(f"Request timed out after {timeout}s")
    except Exception as e:
        raise AIError(f"{provider} error: {str(e)}")


def test_connection(provider: str, api_key: Optional[str] = None) -> bool:
    """Test AI provider connection.
    
    Args:
        provider: AI provider name.
        api_key: API key (for cloud providers).
    
    Returns:
        True if connection successful.
    """
    try:
        if provider == "ollama":
            url = f"{PROVIDERS['ollama']['base_url']}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        else:
            # Just test by making a minimal request
            _cloud_request(provider, "Test", "test-model", api_key, 10)
            return True
    except Exception:
        return False