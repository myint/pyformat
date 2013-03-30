#!/usr/bin/env python

"""Test suite for pyformat."""

import contextlib
import io
import tempfile
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

    def test_format_code_with_aggressive(self):
        self.assertEqual('True\n',
                         pyformat.format_code(
                             unicode('True == True\n'),
                             aggressive=True))

    def test_format_code_without_aggressive(self):
        self.assertEqual('True == True\n',
                         pyformat.format_code(
                             unicode('True == True\n'),
                             aggressive=False))


class TestSystem(unittest.TestCase):

    def test_diff(self):
        with temporary_file('''\
if True == True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', filename],
                          standard_out=output_file,
                          standard_error=None)
            self.assertEqual(unicode('''\
@@ -1,2 +1,2 @@
 if True == True:
-    x = "abc"
+    x = 'abc'
'''), '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_diff_with_aggressive(self):
        with temporary_file('''\
if True == True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', '--aggressive', filename],
                          standard_out=output_file,
                          standard_error=None)
            self.assertEqual(unicode('''\
@@ -1,2 +1,2 @@
-if True == True:
-    x = "abc"
+if True:
+    x = 'abc'
'''), '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_diff_with_empty_file(self):
        with temporary_file('') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', filename],
                          standard_out=output_file,
                          standard_error=None)
            self.assertEqual('', output_file.getvalue())

    def test_diff_with_nonexistent_file(self):
        output_file = io.StringIO()
        pyformat.main(argv=['my_fake_program', 'nonexistent_file'],
                      standard_out=output_file,
                      standard_error=output_file)
        self.assertIn('no such file', output_file.getvalue().lower())

    def test_verbose(self):
        output_file = io.StringIO()
        pyformat.main(argv=['my_fake_program', '--verbose', __file__],
                      standard_out=output_file,
                      standard_error=output_file)
        self.assertIn('.py', output_file.getvalue())

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

    def test_multiple_jobs(self):
        with temporary_file('''\
if True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat.main(argv=['my_fake_program', '--in-place',
                                '--jobs=2', filename],
                          standard_out=output_file,
                          standard_error=None)
            with open(filename) as f:
                self.assertEqual('''\
if True:
    x = 'abc'
''', f.read())

    def test_multiple_jobs_should_require_in_place(self):
        output_file = io.StringIO()
        pyformat.main(argv=['my_fake_program',
                            '--jobs=2', __file__],
                      standard_out=output_file,
                      standard_error=output_file)

        self.assertIn('requires --in-place', output_file.getvalue())

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
