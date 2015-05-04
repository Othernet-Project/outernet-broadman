#!/usr/bin/python

"""
Calculate content directory paths from content IDs

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re
import os

from . import path
from . import conz

pr = conz.Console()

CHUNK = 1000  # process no more than this many paths at once


def convert(*cids):
    if not cids:
        cidsrx = path.pathrx('')
    else:
        cidsrx = '|'.join(path.pathrx(cid) for cid in cids)
    fullrx = re.compile('^{}{}(?:{})$'.format(path.POOLDIR, os.sep, cidsrx))
    matcher = lambda p: fullrx.match(p)
    for p in path.fnwalk(path.POOLDIR, matcher, shallow=True):
        pr.pstd(os.path.abspath(p))


def main():
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
        for cids in pr.readpipe(CHUNK):
            convert(*cids)
