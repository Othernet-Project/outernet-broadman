#!/usr/bin/python

"""
Update content

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import conz
import outernet_metadata.validator as validator

from . import git
from . import path
from . import jsonf


cn = conz.Console()


def remove(cid):
    cdir = path.contentdir(cid)
    git.remove(cdir)


def reset(cid):
    cdir = path.contentdir(cid)
    try:
        git.reset(cdir)
    except ValueError:
        cn.pverr(cid, 'possibly new content, cannot reset')


def revert(cid):
    cdir = path.contentdir(cid)
    try:
        git.revert(cdir)
    except ValueError:
        cn.pverr(cid, 'there is nothing to revert')


def update(cid):
    cdir = path.contentdir(cid)
    if not git.has_changes(cdir):
        cn.pverr(cid, 'nothing to update')
        return
    try:
        data = jsonf.load(path.infopath(cdir))
    except jsonf.LoadError:
        raise ValueError('invalid metadata file')
    # Validate metadata
    ret = validator.validate(data)
    if ret:
        for k, err in ret.items():
            cn.pverr(cid, '{} - {}'.format(k, err.args[0]))
        raise ValueError('invalid metadata')
    # Validate entry point
    index = data.get('index')
    if index and not os.path.exists(os.path.join(cdir, index)):
        cn.pverr(cid, 'index not found at specified path ({})'.format(index))
        raise ValueError('invalid index')
    git.commit_update(cdir)


def main():
    from . import args

    parser = args.getparser(
        'Update or reset content',
        usage='%(prog)s [options] CID [CID...])\n       '
        'CID | %(prog)s [options]')
    parser.add_argument('cids', metavar='CID', nargs='*',
                        help='content ID or content directory path')
    revgrp = parser.add_argument_group('Rollback options')
    revopt = revgrp.add_mutually_exclusive_group()
    revopt.add_argument('--reset', '-r', action='store_true',
                        help='reset all changes instead of updating (cannot '
                        'be used with revert or remove)')
    revopt.add_argument('--revert', '-v', action='store_true',
                        help='revert last set of changes (cannot be used with '
                        'reset or remove)')
    revopt.add_argument('--remove', '-m', action='store_true',
                        help='remove content from pool (cannot be used with '
                        'reset or revert)')
    args = parser.parse_args()

    if cn.interm:
        if not args.cids:
            parser.print_help()
            cn.quit(1)
        src = args.cids
    else:
        src = cn.readpipe()

    # Choose appropriate function based on switches
    if args.reset:
        fn = reset
    elif args.revert:
        fn = revert
    elif args.remove:
        fn = remove
    else:
        fn = update

    for cid in src:
        cid = path.cid(cid.strip())
        try:
            fn(cid)
            cn.pok(cid)
        except ValueError:
            cn.png(cid)


if __name__ == '__main__':
    main()
