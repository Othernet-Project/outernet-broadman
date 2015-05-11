#!/usr/bin/python

"""
Create a new content pool repository

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import conz

from . import git
from . import path


cn = conz.Console()


def create_pool():
    pooldir = os.path.abspath(path.POOLDIR)
    if not os.path.exists(pooldir):
        try:
            os.makedirs(pooldir)
        except OSError as e:
            print(e)
            cn.pverr(pooldir, 'Could not create content pool directory')
            cn.quit(1)
    if not os.path.isdir(pooldir):
        cn.pverr(pooldir, 'Path exists but is not a directory')
        cn.quit(1)
    git.init()


def main():
    from . import args

    parser = args.getparser('Initiaize content pool repository')
    parser.parse_args()
    create_pool()


if __name__ == '__main__':
    main()
