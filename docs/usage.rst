Usage
=====

Basic Commands
--------------

Fast mode (rule-based, no AI):

.. code-block:: bash

   ai-review ./project
   ai-review ./project --mode fast

AI mode with Ollama:

.. code-block:: bash

   ai-review ./project --mode ai --provider ollama --model llama3.1:8b

Cloud mode with API:

.. code-block:: bash

   ai-review ./project --mode cloud --provider deepseek --api-key sk-xxx

Output Formats
--------------

CLI (default):

.. code-block:: bash

   ai-review ./project --format cli

JSON:

.. code-block:: bash

   ai-review ./project --format json --output report.json

HTML:

.. code-block:: bash

   ai-review ./project --format html --output report.html

SARIF (GitHub Code Scanning):

.. code-block:: bash

   ai-review ./project --format sarif --output report.sarif

All Options
-----------

.. code-block:: bash

   -m, --mode [fast|ai|cloud]      Analysis mode
   -p, --provider                   AI provider (ollama, deepseek, etc.)
   -k, --api-key                    API key for cloud mode
   -M, --model                      AI model name
   -o, --output                     Report file path
   -f, --format [cli|json|html|sarif]
                                    Output format
   -s, --severity [critical|warning|info|all]
                                    Minimum severity
   -t, --threads                    Number of parallel threads (default: 4)
   -i, --ignore                     Ignore patterns (comma-separated)
   -v, --verbose                    Show detailed progress
   --help                           Show help message

Examples
--------

Scan with custom settings:

.. code-block:: bash

   ai-review ./project --mode fast --threads 8 --ignore __pycache__,.git

Generate HTML report:

.. code-block:: bash

   ai-review ./project --format html --output report.html --severity warning

CI/CD Integration:

.. code-block:: bash

   ai-review . --mode fast --format sarif --output report.sarif

Single file scan:

.. code-block:: bash

   ai-review file.py --mode fast

Multiple projects:

.. code-block:: bash

   ai-review ./project1 ./project2 --mode fast --format json --output report.json
