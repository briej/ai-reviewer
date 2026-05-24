API Reference
=============

Python API (v1.3.1)
-------------------

Scanner
~~~~~~~

.. automodule:: src.scanner
   :members:
   :undoc-members:
   :show-inheritance:

Analyzer
~~~~~~~~

.. automodule:: src.analyzer
   :members:
   :undoc-members:
   :show-inheritance:

AI Analyzer
~~~~~~~~~~~

.. automodule:: src.ai_analyzer
   :members:
   :undoc-members:
   :show-inheritance:

Cloud Client
~~~~~~~~~~~~

.. automodule:: src.cloud_client
   :members:
   :undoc-members:
   :show-inheritance:

Reporter
~~~~~~~~

.. automodule:: src.reporter
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
~~~~~~~~~~~~~

.. automodule:: src.config
   :members:
   :undoc-members:
   :show-inheritance:

CLI Usage
---------

The CLI is built with Click. Main command:

.. code-block:: python

   from ai_reviewer import main
   main()

Using as Library
----------------

Fast analysis:

.. code-block:: python

   from pathlib import Path
   from src.analyzer import fast_analyze
   from src.scanner import scan_files, read_file

   # Scan files
   files = scan_files("./project")

   # Analyze each file
   for file_path in files:
       content = read_file(file_path)
       issues = fast_analyze(file_path, content)
       for issue in issues:
           print(f"{issue['type']}: {issue['message']}")

AI analysis:

.. code-block:: python

   from src.cloud_client import analyze_with_ai

   results = analyze_with_ai(
       file_path=Path("example.py"),
       content=code,
       initial_issues=[],
       provider="ollama",
       model="llama3.1:8b"
   )

Web API
-------

Base URL: ``http://localhost:8000``

Endpoints:

- ``GET /`` - Home page
- ``POST /api/scan`` - Scan project
- ``GET /api/results/{scan_id}`` - Get results
- ``POST /api/upload`` - Upload file
- ``GET /api/providers`` - List providers
- ``GET /health`` - Health check

See `Web Interface <web-interface.html>`_ for details.

VS Code API
-----------

Commands:

- ``ai-reviewer.scanWorkspace``
- ``ai-reviewer.scanFile``
- ``ai-reviewer.showResults``
- ``ai-reviewer.clearResults``

Settings:

- ``ai-reviewer.mode``
- ``ai-reviewer.provider``
- ``ai-reviewer.model``
- ``ai-reviewer.severity``
- ``ai-reviewer.ignore``

See `VS Code Extension <vscode-extension.html>`_ for details.
