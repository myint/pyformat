#!/usr/bin/env python
"""Setup for pyformat."""

import ast
from distutils import core


def version():
    """Return version string."""
    with open('pyformat.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    core.setup(name='pyformat',
               version=version(),
               description='Formats Python code (using autopep8, '
                           ' docformatter, etc.).',
               long_description=readme.read(),
               license='Expat License',
               author='Steven Myint',
               url='https://github.com/myint/pyformat',
               classifiers=['Intended Audience :: Developers',
                            'Environment :: Console',
                            'Programming Language :: Python :: 2.6',
                            'Programming Language :: Python :: 2.7',
                            'Programming Language :: Python :: 3',
                            'License :: OSI Approved :: MIT License'],
               keywords='strings, formatter, style',
               py_modules=['pyformat'],
               scripts=['pyformat'])
