#!/usr/bin/env python

"""
Match inside JSON data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys

from . import jsonf
from . import data
from . import conz

cn = conz.Console()


def load_file(path):
    try:
        return jsonf.load(path)
    except jsonf.LoadError:
        cn.pverr(path, 'bad metadata file')
        cn.quit(1)


def domatch(path, args):
    path = path.strip()
    if not os.path.basename(path) == 'info.json':
        infopath = os.path.join(path, 'info.json')
    else:
        infopath = path
    d = load_file(infopath)
    if data.match(d, args.key, args.keyword, args.t, xmatch=args.x,
                  icase=args.i, gt=args.gt, lt=args.lt):
        cn.pstd(path)


def main():
    from . import args

    OPTS = '[-h] [-V] [-x] [-i] [-gt] [-lt] [-t TYPE] KEY KEYWORD'
    parser = args.getparser(
        'Match within JSON key values',
        usage='%(prog)s {0} [PATH]\n       PATH | %(prog)s {0}'.format(OPTS))
    parser.add_argument('key', metavar='KEY', help='key within the JSON data')
    parser.add_argument('keyword', metavar='KEYWORD', help='search keyword')
    parser.add_argument('paths', metavar='PATH', help='JSON file or content '
                        'directory (dfaults to info.json in current '
                        'directory, ignored when used in a pipe)',
                        default=['./info.json'], nargs='*')

    # Match type
    parser.add_argument('-x', action='store_true',
                        help='exact match', default=False)
    parser.add_argument('-i', action='store_true',
                        help='ignore case', default=False)
    parser.add_argument('-gt', action='store_true',
                        help='do a greater-than KEYWORD match', default=False)
    parser.add_argument('-lt', action='store_true',
                        help='do a less-than KEYWORD match', default=False)

    # Value type
    parser.add_argument('-t', help='treat KEYWORD as type (d for date in '
                        'YYYY-MM-DD format, t for timestamp in YYYY-MM-DD '
                        'HH:MM:SS format, n for numeric, b for boolean)',
                        metavar='TYPE', default=None)
    args = parser.parse_args(sys.argv[1:])

    if sys.stdin.isatty():
        for path in args.paths:
            domatch(path, args)
    else:
        path = sys.stdin.readline()
        while path:
            domatch(path, args)
            path = sys.stdin.readline()


if __name__ == '__main__':
    main()
