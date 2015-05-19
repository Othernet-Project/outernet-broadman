"""
Functions for working with program arguments

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import platform
import argparse

from . import __version__, __copyright__

VERSION = "%(prog)s {} / Python {} {}".format(
    __version__,
    '.'.join([str(s) for s in sys.version_info[:3]]),
    ' '.join(platform.architecture()))


def getparser(desc, usage=None, has_debug=False, has_verbose=False):
    parser = argparse.ArgumentParser(
        description=desc,
        usage=usage,
        epilog=__copyright__)
    parser.add_argument('--version', '-V', action='version', version=VERSION)
    if has_verbose:
        parser.add_argument('--verbose', '-v', action='store_true',
                            help='enable verbose output')
    if has_debug:
        parser.add_argument('--debug', '-D', action='store_true',
                            help='enable debugging')
    return parser
