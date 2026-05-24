Security Rules
==============

ai-reviewer checks for OWASP Top 10 vulnerabilities and more.

OWASP Top 10 Rules
------------------

SQL Injection
~~~~~~~~~~~~~

Detects unsafe SQL queries with string concatenation.

**Example:**

.. code-block:: python

   # ❌ Vulnerable
   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

   # ✅ Safe
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

Cross-Site Scripting (XSS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detects dangerous DOM manipulation in JavaScript.

**Example:**

.. code-block:: javascript

   // ❌ Vulnerable
   element.innerHTML = userInput

   // ✅ Safe
   element.textContent = userInput

Security Misconfiguration
~~~~~~~~~~~~~~~~~~~~~~~~~

Detects debug mode and insecure settings.

**Example:**

.. code-block:: python

   # ❌ Vulnerable
   DEBUG = True

   # ✅ Safe
   DEBUG = False

Cryptographic Failures
~~~~~~~~~~~~~~~~~~~~~~

Detects weak hashing algorithms.

**Example:**

.. code-block:: python

   # ❌ Weak
   hashlib.md5(password)

   # ✅ Strong
   hashlib.sha256(password)

Additional Security Rules
-------------------------

Command Injection
~~~~~~~~~~~~~~~~~

Detects shell=True with string concatenation.

Path Traversal
~~~~~~~~~~~~~~

Detects unsafe file operations with user input.

XXE (XML External Entity)
~~~~~~~~~~~~~~~~~~~~~~~~~

Detects unsafe XML parsing.

Insecure Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~

Detects pickle usage with untrusted data.

SSRF (Server-Side Request Forgery)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detects unvalidated URL requests.

LDAP Injection
~~~~~~~~~~~~~~

Detects unsafe LDAP queries.

Weak TLS
~~~~~~~~

Detects outdated TLS/SSL versions.

Total Rules
-----------

- **13** security rules
- **3** bug detection rules
- **3** code smell rules
- **2** performance rules

**Total: 21 rules**
