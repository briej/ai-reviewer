🤖 ai-reviewer Documentation
=============================

AI-powered code reviewer with OWASP Top 10 checks. Fast. Local. Configurable.

**Version:** 1.3.1

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   vscode-extension
   web-interface
   security-rules
   ai-providers
   api
   contributing

Features
--------

- ⚡ Works offline (Fast Mode) or with any AI provider (Cloud Mode)
- 🔒 OWASP Top 10 security scanning
- 🚀 Parallel processing (up to 8 threads)
- 📊 HTML / SARIF / JSON / CLI reports
- 🎯 8+ languages supported
- 💻 VS Code extension
- 🌐 Web interface
- 🐳 Docker support

Quick Start
-----------

.. code-block:: bash

   pip install ai-reviewer-cli
   ai-review ./my-project --mode fast

AI Mode
-------

.. code-block:: bash

   # Local AI with Ollama
   ai-review ./project --mode ai --provider ollama --model llama3.1:8b

   # Cloud AI with DeepSeek
   ai-review ./project --mode cloud --provider deepseek --api-key sk-xxx

Output Formats
--------------

.. code-block:: bash

   # CLI (default)
   ai-review ./project

   # JSON
   ai-review ./project --format json --output report.json

   # HTML
   ai-review ./project --format html --output report.html

   # SARIF (GitHub Code Scanning)
   ai-review ./project --format sarif --output report.sarif

Quick Start
-----------

.. code-block:: bash

   pip install ai-reviewer-cli
   ai-review ./my-project --mode fast

Installation
------------

.. include:: installation.rst

Usage
-----

.. include:: usage.rst

Security Rules
--------------

.. include:: security-rules.rst

AI Providers
------------

.. include:: ai-providers.rst

API Reference
-------------

.. include:: api.rst

Contributing
------------

.. include:: contributing.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
