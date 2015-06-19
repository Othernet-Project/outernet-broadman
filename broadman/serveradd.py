#!/usr/bin/python

"""
Add content to server

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import outernet_metadata.validator as validator

import conz

from . import git
from . import path
from . import jsonf
from . import backlog


cn = conz.Console()


def validate_servers(servers, create=False):
    """ Validate server names and if necessary, create server directories """
    for s in servers:
        sdir = path.serverdir(s)
        if ' ' in s:
            cn.pverr(s, 'Server name cannot contain spaces')
            cn.quit(1)
        if os.path.exists(sdir):
            continue
        if create:
            os.makedirs(sdir)
        else:
            cn.pverr(s, 'Server does not exist')
            cn.quit(1)
        if not os.path.isdir(sdir):
            cn.pverr(sdir, 'Server path is not a directory')
            cn.quit(1)


def add_to_servers(cid, servers):
    """ Add content with given cid to the server """
    cdir = path.contentdir(cid)
    ipath = path.infopath(cdir)
    # We only let content that has been fully updated to be added
    if git.has_changes(cdir):
        raise RuntimeError('content has pending changes, please update first')
    # We let the exception from validation propagate up to the caller, and
    # caller is expected to handle this.
    if validator.validate(jsonf.load(ipath)):
        raise RuntimeError('content contains invalid metadata')
    for s in servers:
        target = path.contentdir(cid, server=s)
        if not os.path.islink(target):
            os.symlink(cdir, target)
            git.commit_add_to_server(target, s)
        # We add this to backlog regardless of whether a new symlink is crated.
        # We assume that user wishes to update the content even if symlink
        # already exists.
        backlog.cadd(cid, s)


def main():
    from . import args

    parser = args.getparser(
        'Add content to a server',
        usage='%(prog)s [options] CID [CID...]\n       '
        'CID | %(prog)s [options]')
    parser.add_argument('cids', metavar='CONTENT', nargs='*',
                        help='content ID or path to content directory')
    parser.add_argument('--create', '-c', action='store_true',
                        help='create missing servers')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--servers', '-s', metavar='SERVER', nargs='+',
                          required=True, help='add content to SERVERs')
    args = parser.parse_args()

    validate_servers(args.servers, create=args.create)

    if cn.interm:
        if not args.cids:
            parser.print_help()
            cn.quit(1)
        src = args.cids
    else:
        src = args.readpipe()

    for cid in src:
        cid = path.cid(cid)
        try:
            add_to_servers(cid, servers=args.servers)
            cn.pstd(cn.color.green('{}: OK'.format(cid)))
        except (jsonf.LoadError, RuntimeError) as e:
            cn.pverr(cid, e)
            cn.pstd(cn.color.red('{}: ERR'.format(cid)))


if __name__ == '__main__':
    main()
