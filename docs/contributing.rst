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

Testing
-------

.. code-block:: bash

   # Run tests
   pytest

   # Test with coverage
   pytest --cov=src tests/

   # Run ai-reviewer on itself
   ai-review . --mode fast

Pull Request Process
--------------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a PR

Ideas for Improvement
---------------------

- Support more languages (PHP, Ruby, Kotlin)
- Web interface
- VS Code extension
- Auto-fix vulnerabilities
- Integration with GitLab CI

License
-------

MIT License. See ``LICENSE`` file.
