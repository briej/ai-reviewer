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


def _format_prompt(file_path: Path, content: str, issues: List[Dict[str, Any]]) -> str:
    """Format code and issues for AI analysis."""
    prompt = f"""Analyze the following code for security vulnerabilities and code quality issues.

**File:** {file_path.name}

**Code:**
```{file_path.suffix.lstrip('.')}
{content}
```

**Preliminary findings (from static analysis):**
"""
    
    if issues:
        for issue in issues[:10]:  # Limit to top 10
            prompt += f"- {issue.get('type', 'unknown')}: {issue.get('message', 'No message')} at line {issue.get('location', 'unknown')}\n"
    else:
        prompt += "No issues detected by static analysis.\n"
    
    prompt += """
**Task:**
1. Review the code for security vulnerabilities (OWASP Top 10)
2. Identify false positives in the preliminary findings
3. Find additional issues that static analysis missed
4. Provide specific line numbers and recommendations

**Output format (JSON only):**
{
    "issues": [
        {
            "severity": "critical|warning|info",
            "type": "issue-type",
            "line": 123,
            "message": "Description",
            "recommendation": "How to fix"
        }
    ],
    "false_positives": ["list of incorrect findings"],
    "summary": "Brief summary of findings"
}

Respond with valid JSON only.
"""
    
    return prompt


def analyze_with_ai(
    file_path: Path,
    content: str,
    initial_issues: List[Dict[str, Any]],
    provider: str = "ollama",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
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
        raise AIError("requests library not installed. Install with: pip install requests")
    
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
        raise AIError("Cannot connect to Ollama. Make sure it's running on localhost:11434")
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
        raise AIError("requests library not installed. Install with: pip install requests")
    
    config = PROVIDERS[provider]
    api_key = _get_api_key(provider, api_key)
    
    if not api_key:
        raise AIError(f"No API key for {provider}. Set {provider.upper()}_API_KEY or pass --api-key")
    
    url = f"{config['base_url']}{config['chat_endpoint']}"
    
    headers = {
        "Content-Type": "application/json",
        config["auth_header"]: f"{config['auth_prefix']}{api_key}",
    }
    
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