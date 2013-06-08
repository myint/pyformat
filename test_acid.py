#!/usr/bin/env python
"""Test that pyformat runs without crashing on various Python files."""

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import subprocess


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
PYFORMAT_BIN = os.path.join(ROOT_PATH, 'pyformat')

import autopep8

if sys.stdout.isatty():
    YELLOW = '\x1b[33m'
    END = '\x1b[0m'
else:
    YELLOW = ''
    END = ''


def colored(text, color):
    """Return color coded text."""
    return color + text + END


def readlines(filename):
    """Return contents of file as a list of lines."""
    with autopep8.open_with_encoding(
            filename,
            encoding=autopep8.detect_encoding(filename)) as f:
        return f.readlines()


def diff(before, after):
    """Return diff of two files."""
    import difflib
    return ''.join(difflib.unified_diff(
        readlines(before),
        readlines(after),
        before,
        after))


def run(filename, verbose=False, options=None):
    """Run pyformat on file at filename.

    Return True on success.

    """
    if not options:
        options = []

    import test_pyformat
    with test_pyformat.temporary_directory() as temp_directory:
        temp_filename = os.path.join(temp_directory,
                                     os.path.basename(filename))
        import shutil
        shutil.copyfile(filename, temp_filename)

        if 0 != subprocess.call([PYFORMAT_BIN, '--in-place', temp_filename] +
                                options):
            sys.stderr.write('pyformat crashed on ' + filename + '\n')
            return False

        try:
            file_diff = diff(filename, temp_filename)
            if verbose:
                sys.stderr.write(file_diff)

            if check_syntax(filename):
                try:
                    check_syntax(temp_filename, raise_error=True)
                except (SyntaxError, TypeError,
                        UnicodeDecodeError) as exception:
                    sys.stderr.write('pyformat broke ' + filename + '\n' +
                                     str(exception) + '\n')
                    return False
        except IOError as exception:
            sys.stderr.write(str(exception) + '\n')

    return True


def check_syntax(filename, raise_error=False):
    """Return True if syntax is okay."""
    with autopep8.open_with_encoding(
            filename,
            encoding=autopep8.detect_encoding(filename)) as input_file:
        try:
            compile(input_file.read(), '<string>', 'exec', dont_inherit=True)
            return True
        except (SyntaxError, TypeError, UnicodeDecodeError):
            if raise_error:
                raise
            else:
                return False


def process_args():
    """Return processed arguments (options and positional arguments)."""
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--timeout',
        help='stop testing additional files after this amount of time '
             '(default: %(default)s)',
        default=-1,
        type=float)

    parser.add_argument('--aggressive', action='store_true',
                        help='pass to the pyformat "--aggressive" option')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print verbose messages')

    parser.add_argument('files', nargs='*', help='files to format')

    return parser.parse_args()


class TimeoutException(Exception):

    """Timeout exception."""


def timeout(_, __):
    raise TimeoutException()


def check(args):
    """Run recursively run pyformat on directory of files.

    Return False if the fix results in broken syntax.

    """
    if args.files:
        dir_paths = args.files
    else:
        dir_paths = [path for path in sys.path
                     if os.path.isdir(path)]

    options = []
    if args.aggressive:
        options.append('--aggressive')

    filenames = dir_paths
    completed_filenames = set()

    try:
        import signal
        if args.timeout > 0:
            signal.signal(signal.SIGALRM, timeout)
            signal.alarm(int(args.timeout))

        while filenames:
            try:
                name = os.path.realpath(filenames.pop(0))
                if not os.path.exists(name):
                    # Invalid symlink.
                    continue

                if name in completed_filenames:
                    sys.stderr.write(
                        colored(
                            '--->  Skipping previously tested ' + name + '\n',
                            YELLOW))
                    continue
                else:
                    completed_filenames.update(name)

                if os.path.isdir(name):
                    for root, directories, children in os.walk(name):
                        filenames += [os.path.join(root, f) for f in children
                                      if f.endswith('.py') and
                                      not f.startswith('.')]

                        directories[:] = [d for d in directories
                                          if not d.startswith('.')]
                else:
                    verbose_message = '--->  Testing with ' + name
                    sys.stderr.write(colored(verbose_message + '\n', YELLOW))

                    if not run(os.path.join(name), verbose=args.verbose,
                               options=options):
                        return False
            except (UnicodeDecodeError, UnicodeEncodeError) as exception:
                # Ignore annoying codec problems on Python 2.
                print(exception, file=sys.stderr)
                continue
    except TimeoutException:
        sys.stderr.write('Timed out\n')
    finally:
        if args.timeout > 0:
            signal.alarm(0)

    return True


def main():
    """Run main."""
    return 0 if check(process_args()) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
