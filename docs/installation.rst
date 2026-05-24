Installation
============

Prerequisites
-------------

- Python 3.9 or higher
- pip package manager
- (Optional) Ollama for AI mode

Quick Install
-------------

.. code-block:: bash

   pip install ai-reviewer-cli

Verify installation:

.. code-block:: bash

   ai-review --version

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

For development:

.. code-block:: bash

   pip install ai-reviewer-cli[dev]

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
