#!/usr/bin/python

"""
Calculate content directory paths from content IDs

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import conz

from . import path


cn = conz.Console()

CHUNK = 1000  # process no more than this many paths at once


def convert(server, cids, meta_path=False):
    for p in path.find_contentdirs(cids, server=server):
        if meta_path:
            p = os.path.join(p, 'info.json')
        cn.pstd(os.path.abspath(p))


def main():
    from . import args

    parser = args.getparser(
        'Get content directory path from content ID',
        usage='%(prog)s [options] CID [CID...]\n       '
        'CID | %(prog)s [options]')
    parser.add_argument('cids', metavar='CID', nargs='*',
                        help='full or partial content ID')
    parser.add_argument('--server', '-s', metavar='SERVER',
                        help='server on which to look for paths (default: '
                        '%(default)s', default='master')
    parser.add_argument('--meta', '-m', action='store_true',
                        help='print path to metadata file instead of content '
                        'directory')
    args = parser.parse_args()

    if os.isatty(0):
        convert(args.server, args.cids, args.meta)
    else:
        for cids in cn.readpipe(CHUNK):
            convert(args.server, cids, args.meta)
