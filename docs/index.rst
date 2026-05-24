🤖 ai-reviewer Documentation
=============================

AI-powered code reviewer with OWASP Top 10 checks. Fast. Local. Configurable.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   security-rules
   ai-providers
   api
   contributing

Features
--------

- ⚡ Works offline (Fast Mode) or with any AI provider (Cloud Mode)
- 🔒 OWASP Top 10 security scanning
- 🚀 Parallel processing
- 📊 HTML / SARIF / JSON reports
- 🎯 8+ languages supported

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
