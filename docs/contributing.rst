Contributing
============

We welcome contributions! Here's how to help.

Quick Start
-----------

.. code-block:: bash

   git clone https://github.com/briej/ai-reviewer.git
   cd ai-reviewer
   pip install -e .
   pip install pytest pytest-cov

Running Tests
-------------

.. code-block:: bash

   # Run all tests
   pytest tests/

   # With coverage
   pytest tests/ --cov=src --cov-report=html

   # Specific test
   pytest tests/test_analyzer.py::test_detects_sql_injection -v

Adding Security Rules
---------------------

Edit ``config/rules.json``:

.. code-block:: json

   {
     "security": {
       "new-rule-id": {
         "pattern": "regex-pattern",
         "severity": "warning",
         "message": "Description",
         "example": "How to fix",
         "languages": ["python"]
       }
     }
   }

Adding AI Providers
-------------------

Edit ``src/cloud_client.py``:

.. code-block:: python

   PROVIDERS = {
       "newprovider": {
           "base_url": "https://api.newprovider.com",
           "default_model": "model-name",
           "chat_endpoint": "/v1/chat",
           "auth_header": "Authorization",
           "auth_prefix": "Bearer "
       }
   }

Building Documentation
----------------------

.. code-block:: bash

   cd docs
   pip install -r requirements.txt
   make html

   # Open in browser
   open _build/html/index.html  # macOS/Linux
   start _build/html/index.html  # Windows

VS Code Extension Development
-----------------------------

.. code-block:: bash

   cd vscode-extension
   npm install
   npm run watch  # Watch mode
   npm run compile  # Compile
   vsce package  # Package

Pull Request Process
--------------------

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/amazing-feature``)
3. Make your changes
4. Run tests (``pytest tests/``)
5. Commit changes (``git commit -m 'Add amazing feature'``)
6. Push to branch (``git push origin feature/amazing-feature``)
7. Open Pull Request

Ideas for Improvement
---------------------

- Support more languages (PHP, Ruby, Kotlin, Swift)
- Auto-fix vulnerabilities
- GitLab CI integration
- IntelliJ IDEA plugin
- Real-time monitoring dashboard
- Team collaboration features

License
-------

MIT License. See ``LICENSE`` file.

Contact
-------

- GitHub Issues: https://github.com/briej/ai-reviewer/issues
- Email: (add in README)
