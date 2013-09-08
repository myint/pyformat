#!/usr/bin/env python
"""Setup for pyformat."""

import ast

from setuptools import setup


def version():
    """Return version string."""
    with open('pyformat.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setup(name='pyformat',
          version=version(),
          description='Formats Python code to follow a consistent style.',
          long_description=readme.read(),
          license='Expat License',
          author='Steven Myint',
          url='https://github.com/myint/pyformat',
          classifiers=[
              'Intended Audience :: Developers',
              'Environment :: Console',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Topic :: Software Development :: Libraries :: Python Modules'],
          keywords='beautify, code, format, formatter, reformat, style',
          py_modules=['pyformat'],
          install_requires=['autoflake>=0.4.4',
                            'autopep8>=0.9.4',
                            'docformatter>=0.5.6',
                            'unify>=0.2'],
          scripts=['pyformat'],
          test_suite='test_pyformat')
