pyformat
========

.. image:: https://travis-ci.org/myint/pyformat.png?branch=master
   :target: https://travis-ci.org/myint/pyformat
   :alt: Build status

Formats Python code (using autoflake, autopep8, docformatter, etc.).

Example
-------

After running::

    $ pyformat example.py

this code

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

gets formatted into this

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
