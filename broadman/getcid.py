#!/usr/bin/python

"""
Calcualte a content ID from given path

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import conz

from . import path

cn = conz.Console()


def convert(p):
    cid = path.cid(p)
    if cid:
        cn.pstd(cid)


def main():
    import os
    from . import args

    parser = args.getparser(
        'Return content ID based on given path',
        usage='%(prog)s PATH [-h] [-V]\n       PATH | %(prog)s [-h] [-V]')
    parser.add_argument('paths', metavar='PATH', nargs='*',
                        help='content directory path')
    args = parser.parse_args()

    if os.isatty(0):
        for p in args.paths:
            convert(p)
    else:
        for p in cn.readpipe():
            convert(p.strip())


if __name__ == '__main__':
    main()
