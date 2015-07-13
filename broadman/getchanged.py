#!/usr/bin/python

"""
Get list of content with changes

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import conz

from . import path
from . import git


cn = conz.Console()


def get_changes():
    mdir = path.serverdir()
    return git.Git().git.status(mdir, s=True).split('\n')


def list_changes():
    changes = get_changes()
    cids = (path.cid(c) for c in changes if c)
    for cid in sorted(set(cids)):
        cn.pstd(cid)


def main():
    from . import args

    parser = args.getparser(
        'Get list of content IDs of changed content')
    args = parser.parse_args()

    list_changes()

if __name__ == '__main__':
    main()
