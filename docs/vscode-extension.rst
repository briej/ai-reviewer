VS Code Extension
=================

ai-reviewer has a native VS Code extension for seamless code review.

Installation
------------

From VSIX file:

.. code-block:: bash

   # Download or build the extension
   cd vscode-extension
   vsce package

   # Install locally
   code --install-extension ai-reviewer-vscode-1.3.1.vsix

From source (development):

.. code-block:: bash

   cd vscode-extension
   npm install
   npm run compile
   vsce package
   code --install-extension ai-reviewer-vscode-1.3.1.vsix

Requirements
------------

- **ai-reviewer-cli** must be installed globally:

  .. code-block:: bash

     pip install ai-reviewer-cli

- **Node.js** (for building the extension, optional for usage)

Usage
-----

After installation, use these commands:

1. **Scan Workspace**: ``Ctrl+Shift+P`` → ``ai-reviewer: Scan Workspace``
2. **Scan Current File**: Right-click → ``ai-reviewer: Scan Current File``
3. **Show Results**: ``Ctrl+Shift+P`` → ``ai-reviewer: Show Results``
4. **Clear Results**: ``Ctrl+Shift+P`` → ``ai-reviewer: Clear Results``

Commands
--------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command
     - Description
   * - ``ai-reviewer.scanWorkspace``
     - Scan entire workspace for vulnerabilities
   * - ``ai-reviewer.scanFile``
     - Scan currently open file
   * - ``ai-reviewer.showResults``
     - Display results in webview panel
   * - ``ai-reviewer.clearResults``
     - Clear all results

Settings
--------

Configure in VS Code settings (``settings.json``):

.. code-block:: json

   {
     "ai-reviewer.mode": "fast",
     "ai-reviewer.provider": "ollama",
     "ai-reviewer.model": "llama3.1:8b",
     "ai-reviewer.severity": "all",
     "ai-reviewer.ignore": ["__pycache__", ".git", "node_modules"]
   }

Settings Reference
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Setting
     - Description
   * - ``ai-reviewer.mode``
     - Analysis mode: ``fast``, ``ai``, or ``cloud``
   * - ``ai-reviewer.provider``
     - AI provider: ``ollama``, ``deepseek``, ``openrouter``, ``groq``
   * - ``ai-reviewer.model``
     - AI model name (default: ``llama3.1:8b``)
   * - ``ai-reviewer.severity``
     - Minimum severity: ``critical``, ``warning``, ``info``, ``all``
   * - ``ai-reviewer.ignore``
     - Patterns to ignore during scan

Features
--------

- 🔍 **Real-time scanning** - Scan files as you work
- 📊 **Beautiful results panel** - Webview with dark theme
- ⚙️ **Configurable** - Choose analysis mode and provider
- 🎨 **VS Code integration** - Status bar, context menu, sidebar
- 📈 **Summary dashboard** - Critical, warning, info counts

Screenshots
-----------

Results Panel
~~~~~~~~~~~~~

The extension shows results in a beautiful webview panel with:

- Summary cards (Critical, Warning, Info counts)
- Organized issue list by severity
- Click to navigate to issue location
- Dark theme support

Sidebar View
~~~~~~~~~~~~

Results also appear in the VS Code sidebar under "ai-reviewer" panel.

Context Menu
~~~~~~~~~~~~

Right-click any file in Explorer to scan it individually.

Building the Extension
----------------------

Prerequisites
~~~~~~~~~~~~~

- Node.js v16+
- npm v8+
- @vscode/vsce

Build Steps
~~~~~~~~~~~

.. code-block:: bash

   # Install dependencies
   npm install

   # Compile TypeScript
   npm run compile

   # Package extension
   vsce package

   # Publish (optional)
   vsce publish

Development
~~~~~~~~~~~

Run in watch mode:

.. code-block:: bash

   npm run watch

Debug extension:

1. Open ``vscode-extension/`` folder in VS Code
2. Press ``F5`` to launch extension host
3. Use debugger in the new window

Testing
~~~~~~~

1. Install extension: ``code --install-extension ai-reviewer-vscode-1.3.1.vsix``
2. Open any Python/JavaScript/TypeScript project
3. Run ``ai-reviewer: Scan Workspace``
4. Check results panel

File Structure
--------------

.. code-block:: text

   vscode-extension/
   ├── src/
   │   └── extension.ts      # Main extension code
   ├── out/
   │   ├── extension.js      # Compiled JavaScript
   │   └── extension.js.map  # Source maps
   ├── package.json          # Extension manifest
   ├── tsconfig.json         # TypeScript config
   ├── .vscodeignore         # Files to exclude
   └── README.md             # User documentation

Troubleshooting
---------------

Extension Not Activating
~~~~~~~~~~~~~~~~~~~~~~~~

Make sure ``ai-reviewer-cli`` is installed:

.. code-block:: bash

   pip install ai-reviewer-cli
   ai-review --version

Scan Fails
~~~~~~~~~~

Check that the CLI works:

.. code-block:: bash

   ai-review . --mode fast

If it fails, fix the CLI issue first.

TypeScript Errors
~~~~~~~~~~~~~~~~~

Install dependencies:

.. code-block:: bash

   cd vscode-extension
   npm install

Recompile:

.. code-block:: bash

   npm run compile

See Also
--------

- `VS Code Extension API <https://code.visualstudio.com/api>`_
- `Publishing Extensions <https://code.visualstudio.com/api/working-with-extensions/publishing-extension>`_
- `ai-reviewer CLI <usage.html>`_
