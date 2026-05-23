# 🤖 ai-reviewer

**AI-powered code reviewer with OWASP Top 10 checks. Fast. Local. Configurable.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- ⚡ Works offline (Fast Mode) or with any AI provider (Cloud Mode)
- 🔒 OWASP Top 10 security scanning
- 🚀 Parallel processing
- 📊 HTML / SARIF / JSON reports
- 🎯 8 languages supported

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

---

## 🐳 Docker

Run without installing anything:

```bash
# Build image
docker build -t ai-reviewer https://github.com/briej/ai-reviewer.git#main

# Run analysis on current directory
docker run -v $(pwd):/code ai-reviewer /code --mode fast

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

# Cloud mode — AI-powered analysis
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
      - run: pip install ai-reviewer
      - run: ai-review . --mode fast --format sarif --output report.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: report.sarif
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

---

## 📜 License

MIT
