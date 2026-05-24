# 🤖 ai-reviewer

**AI-powered code reviewer with OWASP Top 10 checks. Fast. Local. Configurable.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- ⚡ Works offline (Fast Mode) or with any AI provider (Cloud Mode)
- 🔒 OWASP Top 10 security scanning
- 🚀 Parallel processing
- 📊 HTML / SARIF / JSON reports
- 🎯 8 languages supported
- 🌐 Web interface available
- 💻 VS Code extension available

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

# AI mode — Ollama-powered analysis (local)
ai-review ./my-project --mode ai --provider ollama --model llama3.1

# Cloud mode — AI-powered analysis (DeepSeek)
ai-review ./my-project --mode cloud --provider deepseek --api-key sk-xxx

# HTML report
ai-review ./my-project --format html --output report.html

# Parallel processing (8 threads)
ai-review ./my-project --threads 8
```

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

```
┌──────────────────────────────────────────────────┐
│ 🤖 ai-reviewer — v1.2                            │
│ OWASP Top 10 | Multi-Cloud | Parallel | Rich CLI │
└──────────────────────────────────────────────────┘

✓ Files found: 23

⚠️  CRITICAL (3)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  hardcoded-secret   config.py:12   Hardcoded secret
  sql-injection      db.py:45       SQL Injection
  code-injection     utils.py:89    eval() is dangerous

🔶 WARNING (7)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  weak-crypto        auth.py:34     Weak hash
  xss                frontend.js:67 innerHTML vulnerable

💡 INFO (12)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  debug              main.py:23     console.log

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

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

### Running Tests

```bash
pytest tests/
```

### Building Documentation

```bash
cd docs
pip install -r requirements.txt
make html
```

Open `docs/_build/html/index.html` in your browser.

### API Documentation

Full API reference available at: https://ai-reviewer.readthedocs.io

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