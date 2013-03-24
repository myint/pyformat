pyformat
========

.. image:: https://travis-ci.org/myint/pyformat.png?branch=master
   :target: https://travis-ci.org/myint/pyformat
   :alt: Build status

Formats Python code (using autopep8, docformatter, etc.).

Example
-------

After running::

    $ pyformat example.py

this code

.. code-block:: python

    x = "abc"
    y = 'hello'

gets formatted into this

.. code-block:: python

    x = 'abc'
    y = 'hello'
