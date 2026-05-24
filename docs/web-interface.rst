Web Interface
=============

ai-reviewer includes a web-based GUI for code review.

Installation
------------

Install with web dependencies:

.. code-block:: bash

   pip install ai-reviewer-cli[web]

Or manually:

.. code-block:: bash

   pip install fastapi uvicorn jinja2

Quick Start
-----------

Start the web server:

.. code-block:: bash

   python web_app.py

Or with uvicorn:

.. code-block:: bash

   uvicorn web_app:app --reload --host 0.0.0.0 --port 8000

Open http://localhost:8000 in your browser.

Features
--------

- 🎨 **Modern UI** - Dark theme, responsive design
- 📊 **Real-time results** - Live scan progress
- 📈 **Summary dashboard** - Critical, warning, info counts
- 📁 **File upload** - Scan individual files
- 🔍 **Project scan** - Scan entire directories
- ⚙️ **Configurable** - Choose mode, provider, model

API Endpoints
-------------

GET /
~~~~~

Home page with web interface.

**Response:** HTML page

POST /api/scan
~~~~~~~~~~~~~~

Scan a project directory.

**Request:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/scan \
     -F "path=/path/to/project" \
     -F "mode=fast" \
     -F "provider=ollama" \
     -F "model=llama3.1:8b"

**Response:**

.. code-block:: json

   {
     "scan_id": "1",
     "summary": {
       "critical": 3,
       "warning": 12,
       "info": 5
     },
     "total_issues": 20
   }

GET /api/results/{scan_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~

Get scan results by ID.

**Response:**

.. code-block:: json

   {
     "scan_id": "1",
     "path": "/path/to/project",
     "mode": "fast",
     "issues": [
       {
         "severity": "critical",
         "type": "sql-injection",
         "location": "db.py:45",
         "message": "SQL Injection via f-string"
       }
     ],
     "summary": {
       "critical": 3,
       "warning": 12,
       "info": 5
     }
   }

POST /api/upload
~~~~~~~~~~~~~~~~

Upload and scan a single file.

**Request:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/upload \
     -F "file=@example.py"

**Response:**

.. code-block:: json

   {
     "filename": "example.py",
     "issues": [...],
     "count": 5
   }

GET /api/providers
~~~~~~~~~~~~~~~~~~

List available AI providers.

**Response:**

.. code-block:: json

   {
     "providers": [
       {"name": "ollama", "type": "local", "default_model": "llama3.1:8b"},
       {"name": "deepseek", "type": "cloud", "default_model": "deepseek-coder"},
       {"name": "openrouter", "type": "cloud", "default_model": "claude-3"},
       {"name": "groq", "type": "cloud", "default_model": "llama3-70b"}
     ]
   }

GET /health
~~~~~~~~~~~

Health check endpoint.

**Response:**

.. code-block:: json

   {"status": "ok", "version": "1.3.1"}

Usage Examples
--------------

Scan Project
~~~~~~~~~~~~

1. Open http://localhost:8000
2. Enter project path: ``/path/to/project``
3. Select mode: ``fast``, ``ai``, or ``cloud``
4. Select provider (for AI/cloud modes)
5. Click "Start Scan"
6. View results in real-time

Upload File
~~~~~~~~~~~

1. Click "Upload File" button
2. Select a file
3. View issues immediately

API Usage
~~~~~~~~~

Python example:

.. code-block:: python

   import requests

   # Scan project
   response = requests.post(
       'http://localhost:8000/api/scan',
       files={'file': open('project.zip', 'rb')},
       data={'mode': 'fast'}
   )
   scan_id = response.json()['scan_id']

   # Get results
   results = requests.get(f'http://localhost:8000/api/results/{scan_id}')
   print(results.json())

cURL example:

.. code-block:: bash

   # Scan project
   curl -X POST http://localhost:8000/api/scan \
     -F "path=/path/to/project" \
     -F "mode=fast"

   # Get results
   curl http://localhost:8000/api/results/1

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Variable
     - Description
   * - ``AI_REVIEWER_MODE``
     - Default analysis mode (fast, ai, cloud)
   * - ``AI_REVIEWER_PROVIDER``
     - Default AI provider (ollama, deepseek, etc.)
   * - ``AI_REVIEWER_MODEL``
     - Default AI model (llama3.1:8b)
   * - ``AI_REVIEWER_PORT``
     - Server port (default: 8000)

Server Configuration
~~~~~~~~~~~~~~~~~~~~

Run with custom settings:

.. code-block:: bash

   # Custom port
   uvicorn web_app:app --port 3000

   # Custom host
   uvicorn web_app:app --host 0.0.0.0

   # Production mode
   uvicorn web_app:app --workers 4 --host 0.0.0.0 --port 8000

Architecture
------------

Components
~~~~~~~~~~

.. code-block:: text

   web_app.py
   ├── FastAPI app
   ├── API endpoints (/api/scan, /api/results, etc.)
   └── Static file serving

   templates/
   └── index.html    # Web interface UI

   static/
   └── (future CSS/JS assets)

   src/
   ├── analyzer.py      # Core analysis engine
   ├── scanner.py       # File scanner
   └── reporter.py      # Report generators

Security
--------

The web interface runs locally by default. For production:

1. Use HTTPS
2. Add authentication
3. Limit file upload size
4. Validate input paths

Example with authentication:

.. code-block:: bash

   pip install python-jose[cryptography]

Then add JWT middleware to ``web_app.py``.

Troubleshooting
---------------

Port Already in Use
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Find process using port 8000
   netstat -ano | findstr :8000

   # Kill process
   taskkill /PID <PID> /F

   # Or use different port
   uvicorn web_app:app --port 3000

Module Not Found
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -U ai-reviewer-cli[web]

Ollama Connection Error
~~~~~~~~~~~~~~~~~~~~~~~

Make sure Ollama is running:

.. code-block:: bash

   ollama list
   ollama pull llama3.1:8b

See Also
--------

- `FastAPI Documentation <https://fastapi.tiangolo.com/>`_
- `ai-reviewer CLI <usage.html>`_
- `VS Code Extension <vscode-extension.html>`_
