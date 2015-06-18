#!/usr/bin/env python

"""
Match inside JSON data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re

import conz

from . import path
from . import data
from . import jsonf

cn = conz.Console()

SIZES = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
}

def load_file(p):
    try:
        return jsonf.load(p)
    except jsonf.LoadError:
        cn.pverr(p, 'bad metadata file')
        cn.quit(1)


def size(p, size, invert=False):
    if os.path.basename(p) == 'info.json':
        path = p[:-9]
    else:
        p = os.path.join(p, 'info.json')
        path = p
    try:
        # Finds the first non-digit, finds the first character of those, and
        # slices that first character out of size
        bytesize = size[re.search('\D', size).span()[0]].lower()
    except AttributeError:
        bytesize = 'b'
    val = int(re.search('\d', size).group(0)) * SIZES[bytesize]
    if data.sizematch(path, val, invert):
        cn.pstd(p)


def domatch(p, args):
    infopath = path.infopath(p)
    d = load_file(infopath)
    if data.match(d, args.key, args.keyword, args.t, xmatch=args.x,
                  icase=args.i, gt=args.gt, lt=args.lt, invert=args.exclude):
        cn.pstd(p)


def main():
    from . import args

    OPTS = '[-h] [-V] [-x] [-i] [-gt] [-lt] [-t TYPE] KEY KEYWORD'
    parser = args.getparser(
        'Match within JSON key values',
        usage='%(prog)s {0} [PATH]\n       PATH | %(prog)s {0}'.format(OPTS))
    parser.add_argument('key', metavar='KEY', help='key within the JSON data -'
                        ' also takes "size" which finds anything larger than '
                        'the keyword which looks like "10Kb"')
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
    parser.add_argument('-e', '--exclude', action='store_true',
                        help='return everything that does NOT match this query',
                        default=False)

    # Value type
    parser.add_argument('-t', help='treat KEYWORD as type (d for date in '
                        'YYYY-MM-DD format, t for timestamp in YYYY-MM-DD '
                        'HH:MM:SS format, n for numeric, b for boolean)',
                        metavar='TYPE', default=None)
    args = parser.parse_args()

    if cn.interm:
        src = args.paths
    else:
        src = cn.readpipe()

    for p in src:
        if args.key == 'size':
            size(p.strip(), args.keyword, args.exclude)
        else:
            domatch(p.strip(), args)


if __name__ == '__main__':
    main()
