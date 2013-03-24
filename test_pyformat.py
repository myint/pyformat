#!/usr/bin/env python

"""Test suite for pyformat."""

import contextlib
import io
import tempfile

try:
    # Python 2.6
    import unittest2 as unittest
except ImportError:
    import unittest

import pyformat


try:
    unicode
except NameError:
    unicode = str


class TestUnits(unittest.TestCase):

    def test_format_code(self):
        self.assertEqual("x = 'abc' \\\n    'next'\n",
                         pyformat.format_code(
                             unicode('x = "abc" \\\n"next"\n')))


class TestSystem(unittest.TestCase):

    def test_diff(self):
        with temporary_file('''\
if True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', filename],
                          standard_out=output_file,
                          standard_error=None)
            self.assertEqual(unicode('''\
@@ -1,2 +1,2 @@
 if True:
-    x = "abc"
+    x = 'abc'
'''), '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_in_place(self):
        with temporary_file('''\
if True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', '--in-place', filename],
                          standard_out=output_file,
                          standard_error=None)
            with open(filename) as f:
                self.assertEqual('''\
if True:
    x = 'abc'
''', f.read())

    def test_ignore_hidden_directories(self):
        with temporary_directory() as directory:
            with temporary_directory(prefix='.',
                                     directory=directory) as inner_directory:

                with temporary_file("""\
if True:
    x = "abc"
""", directory=inner_directory):

                    output_file = io.StringIO()
                    pyformat.main(argv=['my_fake_program',
                                        '--recursive',
                                        directory],
                                  standard_out=output_file,
                                  standard_error=None)
                    self.assertEqual(
                        '',
                        output_file.getvalue().strip())


@contextlib.contextmanager
def temporary_file(contents, directory='.', prefix=''):
    """Write contents to temporary file and yield it."""
    f = tempfile.NamedTemporaryFile(suffix='.py', prefix=prefix,
                                    delete=False, dir=directory)
    try:
        f.write(contents.encode('utf8'))
        f.close()
        yield f.name
    finally:
        import os
        os.remove(f.name)


@contextlib.contextmanager
def temporary_directory(directory='.', prefix=''):
    """Create temporary directory and yield its path."""
    temp_directory = tempfile.mkdtemp(prefix=prefix, dir=directory)
    try:
        yield temp_directory
    finally:
        import shutil
        shutil.rmtree(temp_directory)


if __name__ == '__main__':
    unittest.main()
