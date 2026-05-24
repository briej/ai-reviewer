AI Providers
============

ai-reviewer supports multiple AI providers for enhanced code analysis.

Supported Providers
-------------------

Ollama (Local)
~~~~~~~~~~~~~~

- **Cost**: Free
- **Setup**: Install Ollama locally
- **Models**: llama3.1, llama3.2, codellama, etc.
- **Privacy**: 100% local, no data leaves your machine

Setup:

.. code-block:: bash

   # Install Ollama from https://ollama.ai
   ollama pull llama3.1:8b
   ai-review ./project --mode ai --provider ollama --model llama3.1:8b

DeepSeek
~~~~~~~~

- **Cost**: 1M free tokens/month
- **Setup**: Get API key
- **Model**: deepseek-coder
- **Privacy**: Data sent to DeepSeek

Setup:

.. code-block:: bash

   # Get API key from https://platform.deepseek.com
   export DEEPSEEK_API_KEY=sk-xxx
   ai-review ./project --mode cloud --provider deepseek

OpenRouter
~~~~~~~~~~

- **Cost**: Rate limited free tier
- **Setup**: Get API key
- **Models**: Multiple (Claude, GPT, etc.)
- **Privacy**: Data sent to OpenRouter

Setup:

.. code-block:: bash

   # Get API key from https://openrouter.ai
   export OPENROUTER_API_KEY=sk-xxx
   ai-review ./project --mode cloud --provider openrouter

Groq
~~~~

- **Cost**: Rate limited free tier
- **Setup**: Get API key
- **Model**: Fast inference
- **Privacy**: Data sent to Groq

Setup:

.. code-block:: bash

   # Get API key from https://console.groq.com
   export GROQ_API_KEY=sk-xxx
   ai-review ./project --mode cloud --provider groq

Other Providers
~~~~~~~~~~~~~~~

- **Kimi**: Trial available
- **Qwen**: Trial available

Comparison
----------

+------------+--------------+------------+----------+----------------+
| Provider   | Free Tier    | Speed      | Privacy  | Best For       |
+============+==============+============+==========+================+
| Ollama     | Unlimited    | Medium     | Local    | Development    |
+------------+--------------+------------+----------+----------------+
| DeepSeek   | 1M tokens    | Fast       | Cloud    | Production     |
+------------+--------------+------------+----------+----------------+
| OpenRouter | Rate limited | Fast       | Cloud    | Multi-model    |
+------------+--------------+------------+----------+----------------+
| Groq       | Rate limited | Very Fast  | Cloud    | Speed          |
+------------+--------------+------------+----------+----------------+
| Kimi       | Trial        | Medium     | Cloud    | Chinese code   |
+------------+--------------+------------+----------+----------------+
| Qwen       | Trial        | Medium     | Cloud    | Alibaba eco    |
+------------+--------------+------------+----------+----------------+

Recommended Models
------------------

- **Ollama**: ``llama3.1:8b``, ``llama3.2:3b``, ``codellama:7b``
- **DeepSeek**: ``deepseek-coder``
- **OpenRouter**: ``anthropic/claude-3.5-sonnet``, ``meta-llama/llama-3.1-70b``
- **Groq**: ``llama3-70b``, ``mixtral-8x7b``

Environment Variables
---------------------

Set API keys for cloud providers:

.. code-block:: bash

   # Windows (PowerShell)
   $env:DEEPSEEK_API_KEY="sk-xxx"
   $env:OPENROUTER_API_KEY="sk-xxx"
   $env:GROQ_API_KEY="sk-xxx"

   # Linux/macOS
   export DEEPSEEK_API_KEY=sk-xxx
   export OPENROUTER_API_KEY=sk-xxx
   export GROQ_API_KEY=sk-xxx
