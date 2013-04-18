========
pyformat
========

.. image:: https://travis-ci.org/myint/pyformat.png?branch=master
   :target: https://travis-ci.org/myint/pyformat
   :alt: Build status

.. image:: https://coveralls.io/repos/myint/pyformat/badge.png?branch=master
   :target: https://coveralls.io/r/myint/pyformat
   :alt: Test coverage status

*pyformat* formats Python code to follow a consistent style.


Features
========

- Formats code to follow the PEP 8 style guide (using autopep8_).
- Removes unused imports (using autoflake_).
- Formats docstrings to follow PEP 257 (using docformatter_).
- Makes strings all use the same type of quote where possible (using unify_).


Installation
============

From pip::

    $ pip install --upgrade pyformat


Example
=======

After running::

    $ pyformat --in-place example.py

This code:

.. code-block:: python

   def launch_rocket   ():



       """Launch
   the
   rocket. Go colonize space."""

   def factorial(x):
       '''

       Return x factorial.

       This uses math.factorial.

       '''
       import math
       import re
       import os
       return math.factorial( x );
   def print_factorial(x):
       """Print x factorial"""
       print( factorial(x)  )
   def main():
       """Main
       function"""
       print_factorial(5)
       if factorial(10):
         launch_rocket()

Gets formatted into this:

.. code-block:: python

   def launch_rocket():
       """Launch the rocket.

       Go colonize space.

       """


   def factorial(x):
       """Return x factorial.

       This uses math.factorial.

       """
       import math
       return math.factorial(x)


   def print_factorial(x):
       """Print x factorial."""
       print(factorial(x))


   def main():
       """Main function."""
       print_factorial(5)
       if factorial(10):
           launch_rocket()


.. _autoflake: https://github.com/myint/autoflake
.. _autopep8: https://github.com/hhatto/autopep8
.. _docformatter: https://github.com/myint/docformatter
.. _unify: https://github.com/myint/unify
