#!/usr/bin/env python

# Copyright (C) 2013-2017 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Formats Python code to follow a consistent style."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import signal
import sys

import autoflake
import autopep8
import docformatter
import unify


__version__ = '0.7'


def formatters(aggressive, apply_config, filename='',
               remove_all_unused_imports=False, remove_unused_variables=False):
    """Return list of code formatters."""
    if aggressive:
        yield lambda code: autoflake.fix_code(
            code,
            remove_all_unused_imports=remove_all_unused_imports,
            remove_unused_variables=remove_unused_variables)

        autopep8_options = autopep8.parse_args(
            [filename] + int(aggressive) * ['--aggressive'],
            apply_config=apply_config)
    else:
        autopep8_options = autopep8.parse_args(
            [filename], apply_config=apply_config)

    yield lambda code: autopep8.fix_code(code, options=autopep8_options)
    yield docformatter.format_code
    yield unify.format_code


def format_code(source, aggressive=False, apply_config=False, filename='',
                remove_all_unused_imports=False,
                remove_unused_variables=False):
    """Return formatted source code."""
    formatted_source = source

    for fix in formatters(
            aggressive, apply_config, filename,
            remove_all_unused_imports, remove_unused_variables):
        formatted_source = fix(formatted_source)

    return formatted_source


def format_file(filename, args, standard_out):
    """Run format_code() on a file.

    Return True if the new formatting differs from the original.

    """
    encoding = autopep8.detect_encoding(filename)
    with autopep8.open_with_encoding(filename,
                                     encoding=encoding) as input_file:
        source = input_file.read()

    if not source:
        return False

    formatted_source = format_code(
        source,
        aggressive=args.aggressive,
        apply_config=args.config,
        filename=filename,
        remove_all_unused_imports=args.remove_all_unused_imports,
        remove_unused_variables=args.remove_unused_variables)

    if source != formatted_source:
        if args.in_place:
            with autopep8.open_with_encoding(filename, mode='w',
                                             encoding=encoding) as output_file:
                output_file.write(formatted_source)
        else:
            diff = autopep8.get_diff_text(
                io.StringIO(source).readlines(),
                io.StringIO(formatted_source).readlines(),
                filename)
            standard_out.write(''.join(diff))

        return True

    return False


def _format_file(parameters):
    """Helper function for optionally running format_file() in parallel."""
    (filename, args, _, standard_error) = parameters

    standard_error = standard_error or sys.stderr

    if args.verbose:
        print('{0}: '.format(filename), end='', file=standard_error)

    try:
        changed = format_file(*parameters[:-1])
    except IOError as exception:
        print('{}'.format(exception), file=standard_error)
        return False
    except KeyboardInterrupt:  # pragma: no cover
        return False  # pragma: no cover

    if args.verbose:
        print('changed' if changed else 'unchanged', file=standard_error)

    return changed


def format_multiple_files(filenames, args, standard_out, standard_error):
    """Format files.

    Optionally format files recursively.

    """
    filenames = autopep8.find_files(list(filenames),
                                    args.recursive,
                                    args.exclude_patterns)
    if args.jobs > 1:
        import multiprocessing
        pool = multiprocessing.Pool(args.jobs)

        # We pass neither standard_out nor standard_error into "_format_file()"
        # since multiprocessing cannot serialize io.
        result = pool.map(_format_file,
                          [(name, args, None, None) for name in filenames])
    else:
        result = [_format_file((name, args, standard_out, standard_error))
                  for name in filenames]

    return any(result)


def parse_args(argv):
    """Return parsed arguments."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='pyformat')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument('-a', '--aggressive', action='count', default=0,
                        help='use more aggressive formatters')
    parser.add_argument('--remove-all-unused-imports', action='store_true',
                        help='remove all unused imports, '
                             'not just standard library '
                             '(requires "aggressive")')
    parser.add_argument('--remove-unused-variables', action='store_true',
                        help='remove unused variables (requires "aggressive")')
    parser.add_argument('-j', '--jobs', type=int, metavar='n', default=1,
                        help='number of parallel jobs; '
                             'match CPU count if value is less than 1')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print verbose messages')
    parser.add_argument('--exclude', action='append',
                        dest='exclude_patterns', default=[], metavar='pattern',
                        help='exclude files this pattern; '
                             'specify this multiple times for multiple '
                             'patterns')
    parser.add_argument('--no-config', action='store_false', dest='config',
                        help="don't look for and apply local configuration "
                             'files; if not passed, defaults are updated with '
                             "any config files in the project's root "
                             'directory')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+', help='files to format')

    args = parser.parse_args(argv[1:])

    if args.jobs < 1:
        import multiprocessing
        args.jobs = multiprocessing.cpu_count()

    return args


def _main(argv, standard_out, standard_error):
    """Internal main entry point.

    Return exit status. 0 means no error.

    """
    args = parse_args(argv)

    if args.jobs > 1 and not args.in_place:
        print('parallel jobs requires --in-place',
              file=standard_error)
        return 2

    if not args.aggressive:
        if args.remove_all_unused_imports:
            print('--remove-all-unused-imports requires --aggressive',
                  file=standard_error)
            return 2

        if args.remove_unused_variables:
            print('--remove-unused-variables requires --aggressive',
                  file=standard_error)
            return 2

    format_multiple_files(set(args.files), args, standard_out, standard_error)


def main():
    """Main entry point."""
    try:
        # Exit on broken pipe.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:  # pragma: no cover
        # SIGPIPE is not available on Windows.
        pass

    try:
        return _main(sys.argv,
                     standard_out=sys.stdout,
                     standard_error=sys.stderr)
    except KeyboardInterrupt:  # pragma: no cover
        return 2  # pragma: no cover


if __name__ == '__main__':
    sys.exit(main())
