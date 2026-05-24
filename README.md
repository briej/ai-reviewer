# 🤖 ai-reviewer

**AI-powered code reviewer with OWASP Top 10 checks and context awareness. Fast. Local. Configurable.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- ⚡ **Fast Mode** — Works offline, instant analysis
- 🧠 **Context-Aware Mode** — Cross-file analysis, dependency graph (NEW!)
- 🔒 OWASP Top 10 security scanning
- 🚀 Parallel processing
- 📊 HTML / SARIF / JSON reports
- 🎯 8+ languages supported
- 🌐 Web interface available
- 💻 VS Code extension available

---

## 🆕 What's New in v1.4

### 🧠 Context-Aware Analysis

ai-reviewer now understands your project structure and performs cross-file analysis:

```bash
# Build project graph and analyze with context
ai-review ./project --mode context --cache-graph

# Cache graph for faster subsequent runs
ai-review ./project --mode context
```

**Features:**
- **Cross-file dependency analysis** — Understands imports and data flows
- **False positive reduction** — AI reviews findings with project context
- **Entry point detection** — Identifies routes, main functions, API endpoints
- **Project type detection** — Web app, data science, infrastructure, library
- **Related file context** — AI considers connected files during analysis

### 🎯 Improved AI Prompts

- Better structured output with evidence and recommendations
- CWE references for security issues
- Confidence scoring for each finding
- Actionable fixes with code examples

### ⚡ Performance

- Graph caching for faster repeated scans
- Smarter Ollama model selection (llama3.2:8b for speed)
- Parallel processing in all modes

---

## 💻 VS Code Extension

Install from [VS Code Marketplace](https://marketplace.visualstudio.com) (coming soon!) or manually:

```bash
# Install ai-reviewer-cli first
pip install ai-reviewer-cli

# Build extension
cd vscode-extension
npm install
npm run compile

# Package extension
npm install -g @vscode/vsce
vsce package

# Install locally
code --install-extension ai-reviewer-vscode-1.3.1.vsix
```

**Features:**
- 🔍 Scan entire workspace
- 📄 Scan current file
- 📊 Beautiful results panel
- ⚙️ Configurable in settings

**Commands:**
- `ai-reviewer: Scan Workspace`
- `ai-reviewer: Scan Current File`
- `ai-reviewer: Show Results`

See [vscode-extension/README.md](vscode-extension/README.md) for full documentation.

---

## 🚀 Installation

```bash
pip install ai-reviewer-cli
```

Or from source:

```bash
git clone https://github.com/briej/ai-reviewer.git
cd ai-reviewer
pip install -e .
```

For web interface:

```bash
pip install ai-reviewer-cli[web]
```

---

## 🌐 Web Interface

Run the web interface:

```bash
# Install dependencies
pip install ai-reviewer-cli[web]

# Start web server
python web_app.py

# Or with uvicorn
uvicorn web_app:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

Features:
- 🎨 Beautiful UI with dark mode
- 📊 Real-time scan results
- 📈 Summary dashboard
- 📁 File upload support

---

## 🤖 AI Mode

Use AI-powered analysis with Ollama or cloud providers:

```bash
# Ollama (local, free)
ai-review ./project --mode ai --provider ollama --model llama3.1

# DeepSeek (cloud, 1M free tokens)
ai-review ./project --mode cloud --provider deepseek --api-key sk-xxx

# OpenRouter (Anthropic Claude)
ai-review ./project --mode cloud --provider openrouter --api-key sk-xxx

# Groq (fast inference)
ai-review ./project --mode cloud --provider groq --api-key sk-xxx
```

**Supported AI Providers:**
- **Ollama** - Local, unlimited, free (install separately)
- **DeepSeek** - 1M free tokens/month
- **OpenRouter** - Rate limited free tier
- **Groq** - Rate limited free tier
- **Kimi** - Trial available
- **Qwen** - Trial available

---

## 🐳 Docker

Run without installing anything:

```bash
# Build image
docker build -t ai-reviewer .

# Run analysis on current directory
docker run -v $(pwd):/code ai-reviewer /code --mode fast

# AI mode with Ollama (requires Ollama running on host)
docker run -v $(pwd):/code --add-host host.docker.internal:host-gateway ai-reviewer /code --mode ai --provider ollama --model llama3.1

# Generate HTML report
docker run -v $(pwd):/code ai-reviewer /code --mode fast --format html --output /code/report.html

# With custom config
docker run -v $(pwd):/code -v $(pwd)/.ai-reviewer.yaml:/app/.ai-reviewer.yaml ai-reviewer /code
```

---

## 🎯 Quick Start

```bash
# Fast mode — instant analysis, no AI needed
ai-review ./my-project

# Context mode — cross-file analysis with Ollama (RECOMMENDED)
ai-review ./my-project --mode context --cache-graph

# AI mode — Ollama-powered analysis (local, no context)
ai-review ./my-project --mode ai --provider ollama --model llama3.2

# Cloud mode — AI-powered analysis (DeepSeek)
ai-review ./my-project --mode cloud --provider deepseek --api-key sk-xxx

# HTML report
ai-review ./my-project --format html --output report.html

# Parallel processing (8 threads)
ai-review ./my-project --threads 8
```

### Mode Comparison

| Mode | Speed | Accuracy | Context | Best For |
|------|-------|----------|---------|----------|
| **fast** | ⚡ Instant | 65% | ❌ No | CI/CD, pre-commit |
| **ai** | 🐌 10-60s/file | 80% | ❌ No | Single file review |
| **context** | 🐌🐌 30-90s/file | 85% | ✅ Yes | Deep analysis, PR review |
| **cloud** | 🐌 5-30s/file | 85% | ❌ No | When Ollama unavailable |

---

## 🔥 Features

### Security (OWASP Top 10)
- SQL Injection detection
- XSS vulnerability scanning
- Hardcoded secrets detection
- Weak cryptography checks
- CSRF protection validation

### AI Providers
| Provider | Free Tier | Setup |
|----------|-----------|-------|
| **Ollama** | ✅ Unlimited | Local install |
| **DeepSeek** | ✅ 1M tokens | API key |
| **OpenRouter** | ✅ Rate limited | API key |
| **Kimi** | ✅ Trial | API key |
| **Qwen** | ✅ Trial | API key |
| **Groq** | ✅ Rate limited | API key |

### Output Formats
- **CLI** — Rich terminal output with tables
- **JSON** — Machine-readable
- **HTML** — Beautiful web report
- **SARIF** — GitHub Code Scanning compatible

### Supported Languages
Python, JavaScript, TypeScript, SQL, Go, Java, Rust, C/C++

---

## 📋 Usage Examples

### Basic
```bash
ai-review ./project
```

### Context-Aware Analysis (NEW!)
```bash
# Full context analysis with graph caching
ai-review ./project --mode context --cache-graph

# Use cached graph for faster subsequent runs
ai-review ./project --mode context
```

### Cloud with specific model
```bash
ai-review ./project \
  --mode cloud \
  --provider openrouter \
  --model qwen/qwen-2.5-coder-32b \
  --api-key sk-xxx
```

### CI/CD Integration
```bash
ai-review . --mode fast --format sarif --output report.sarif
```

### Filter severity
```bash
ai-review ./project --severity critical
```

### Ignore patterns
```bash
ai-review ./project --ignore __pycache__ --ignore .git --ignore node_modules
```

---

## ⚙️ Configuration

Create `.ai-reviewer.yaml` in your project root:

```yaml
mode: fast
threads: 4
severity: all

ignore:
  - __pycache__
  - .git
  - node_modules
  - "*.min.js"

cloud:
  provider: deepseek
  model: deepseek-coder
  timeout: 30

rules:
  - id: no-print
    pattern: "print("
    severity: info
    message: "Remove print statements"
    languages: [python]
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Analysis mode (fast, ai, context, cloud) | `fast` |
| `--provider` | AI provider (ollama, deepseek, etc.) | `ollama` |
| `--model` | AI model name | `llama3.2` |
| `--output` | Report file path | - |
| `--format` | Output format (cli, json, html, sarif) | `cli` |
| `--severity` | Minimum severity (critical, warning, info, all) | `all` |
| `--threads` | Parallel workers | `4` |
| `--ignore` | Patterns to ignore | - |
| `--verbose` | Show detailed progress | `False` |
| `--cache-graph` | Cache project graph | `False` |
| `--no-context` | Disable context analysis | `False` |

---

## 🔄 GitHub Actions

```yaml
name: Code Review
on: [push, pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ai-reviewer-cli
      - run: ai-review . --mode fast --format sarif --output report.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: report.sarif
```

**AI-Powered CI/CD:**

```yaml
- run: pip install ai-reviewer-cli
- run: ai-review . --mode ai --provider ollama --model llama3.1 --format sarif --output report.sarif
```

---

## 🛠 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/briej/ai-reviewer
    rev: v1.2
    hooks:
      - id: ai-reviewer
```

---

## 📊 Example Output

### Fast Mode
```
┌──────────────────────────────────────────────────┐
│ 🤖 ai-reviewer — v1.4                            │
│ OWASP Top 10 | Context-Aware | Local AI | Parallel│
└──────────────────────────────────────────────────┘

✓ Files found: 23

⚠️  CRITICAL (3)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Severity   Type             Location        Message
  CRITICAL   hardcoded-secret config.py:12   Hardcoded secret
             → Use os.getenv('SECRET_KEY')
  CRITICAL   sql-injection    db.py:45       SQL Injection via f-string
             → Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
  CRITICAL   code-injection   utils.py:89    eval() is dangerous
             → Use ast.literal_eval() for safe evaluation

🔶 WARNING (7)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Severity   Type        Location     Message
  WARNING    weak-crypto auth.py:34   Weak hash (MD5)
             → Use SHA-256, bcrypt, or Argon2
  WARNING    xss         frontend.js:67 innerHTML vulnerable
             → Use textContent instead

💡 INFO (12)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Severity   Type     Location    Message
  INFO       debug    main.py:23  console.log found
             → Remove before production

──────────────────────────────────────────────────
┌────────────────┬───────┐
│ Files analyzed │ 23/23 │
│ Time           │ 0.45s │
│ Critical       │ 3     │
│ Warning        │ 7     │
│ Info           │ 12    │
│ Score          │ 4.2/10│
└────────────────┴───────┘
```

### Context Mode (with AI recommendations)
```
✓ Files found: 23
✓ Building project context...
✓ Graph cached at .ai-reviewer-graph.json

⚠️  CRITICAL (2) — 1 false positive removed by AI
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Severity   Type          Location        Message
  CRITICAL   sql-injection db.py:45        SQL Injection
             Evidence: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
             Recommendation: Use parameterized queries
             CWE: CWE-89
             Confidence: 0.95

  CRITICAL   xss           frontend.ts:112 Cross-site scripting
             Evidence: element.innerHTML = userInput
             Recommendation: Use textContent or DOMPurify
             CWE: CWE-79
             Confidence: 0.88
```

---

## 📚 Documentation

Full documentation available at: https://ai-reviewer.readthedocs.io

**Contents:**
- 📖 Installation guide
- 🛠 Usage examples
- 💻 VS Code Extension
- 🌐 Web Interface
- 🔒 Security rules
- 🤖 AI providers
- 📊 API reference

Build locally:

```bash
cd docs
pip install -r requirements.txt
make html
open docs/_build/html/index.html
```

---

## 📜 License

MIT
PS> cd ai-reviewer; ai-review . --mode ai --provider ollama --model llama3.2-vision:11b --verbose
#< CLIXML
┌───────────────────────────────────────────────────────────────┐
│ 🤖 ai-reviewer — v1.3                                         │
│ OWASP Top 10 | AI-Powered | Multi-Cloud | Parallel | Rich CLI │
└───────────────────────────────────────────────────────────────┘
⠙ Scanning files...
✓ Files found: 10
  ✗ ai_reviewer.py: Request timed out after 60s
  ✓ __init__.py

Выполняется
Переместить в фоновый режим