API Reference
=============

Python API
----------

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

AI Analysis
-----------

.. code-block:: python

   from src.cloud_client import analyze_with_ai

   results = analyze_with_ai(
       file_path=Path("example.py"),
       content=code,
       initial_issues=[],
       provider="ollama",
       model="llama3.1:8b"
   )
