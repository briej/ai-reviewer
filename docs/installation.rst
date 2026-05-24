Installation
============

Prerequisites
-------------

- Python 3.9 or higher
- pip package manager
- (Optional) Ollama for AI mode
- (Optional) Node.js for VS Code extension

Quick Install
-------------

.. code-block:: bash

   pip install ai-reviewer-cli

Verify installation:

.. code-block:: bash

   ai-review --version
   # Output: ai-reviewer — v1.3.1

Install from Source
-------------------

.. code-block:: bash

   git clone https://github.com/briej/ai-reviewer.git
   cd ai-reviewer
   pip install -e .

Optional Dependencies
---------------------

For web interface:

.. code-block:: bash

   pip install ai-reviewer-cli[web]
   # or
   pip install fastapi uvicorn jinja2

For development:

.. code-block:: bash

   pip install ai-reviewer-cli[dev]
   # or
   pip install pytest pytest-cov black flake8

For VS Code extension (building only):

.. code-block:: bash

   npm install -g @vscode/vsce

AI Mode Setup
-------------

For local AI analysis, install Ollama:

1. Download from https://ollama.ai
2. Install Ollama
3. Pull a model:

   .. code-block:: bash

      ollama pull llama3.1:8b

For cloud AI providers, get API keys:

- **DeepSeek**: https://platform.deepseek.com
- **OpenRouter**: https://openrouter.ai
- **Groq**: https://console.groq.com

Docker Installation
-------------------

.. code-block:: bash

   # Build image
   docker build -t ai-reviewer .

   # Run analysis
   docker run -v $(pwd):/code ai-reviewer /code --mode fast

   # AI mode with Ollama
   docker run -v $(pwd):/code --add-host host.docker.internal:host-gateway \
     ai-reviewer /code --mode ai --provider ollama --model llama3.1:8b
