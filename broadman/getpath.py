#!/usr/bin/python

"""
Calculate content directory paths from content IDs

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import re
import os
import sys
from . import path

CHUNK = 1000  # process no more than this many paths at once


def convert(*cids):
    if not cids:
        cidsrx = path.pathrx('')
    else:
        cidsrx = '|'.join(path.pathrx(cid) for cid in cids)
    fullrx = re.compile('^{}{}(?:{})$'.format(path.POOLDIR, os.sep, cidsrx))
    matcher = lambda p: fullrx.match(p)
    for p in path.fnwalk(path.POOLDIR, matcher, shallow=True):
        print(os.path.abspath(p), file=sys.stdout)


def main():
    import sys
    from . import args

    parser = args.getparser(
        'Get content directory path from content ID',
        usage='%(prog)s [-h] [-V] CID [CID...]\n       CID | %(prog)s')
    parser.add_argument('cids', metavar='CID', nargs='*',
                        help='full or partial content ID')
    args = parser.parse_args()

    if os.isatty(0):
        convert(*args.cids)
    else:
        cids = []
        while True:
            cid = sys.stdin.readline()
            cids.append(cid)
            if len(cids) == CHUNK or not cid:
                convert(*cids)
                cids = []
            if not cid:
                sys.exit(0)
