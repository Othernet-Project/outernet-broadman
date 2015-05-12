#!/usr/bin/python

"""
Remove content from server

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import conz

from . import git
from . import path
from . import backlog


cn = conz.Console()


def validate_servers(servers):
    for s in servers:
        sdir = path.serverdir(s)
        if os.path.isdir(sdir):
            continue
        cn.pverr(sdir, 'Not a server directory')
        cn.quit(1)


def remove_from_servers(cid, servers, force=False):
    cid = path.cid(cid)
    errors = False
    for s in servers:
        cpath = path.contentdir(cid, server=s)
        if os.path.islink(cpath):
            os.unlink(cpath)
            git.commit_remove_from_server(cpath, s)
        else:
            if not force:
                errors = True
                cn.pverr(cid, 'Not found on {}'.format(s))
                continue
        backlog.cdel(cid, s)
    return errors


def main():
    from . import args

    parser = args.getparser(
        'Remove content from servers',
        usage='%(prog)s [options] CID [CID...]\n       '
        'CID | %(prog)s [options]')
    required = parser.add_argument_group('required')
    required = required.add_mutually_exclusive_group(required=True)
    parser.add_argument('cids', metavar='CONTENT', nargs='*',
                        help='content ID or path to content directory')
    required.add_argument('--servers', '-s', metavar='SERVER', nargs='+',
                          help='add content to SERVERs (cannot be used with '
                          '--all)')
    required.add_argument('--all', '-a', action='store_true',
                          help='remove content from all servers (cannot be '
                          'used with --servers)')
    parser.add_argument('--force', '-f', action='store_true',
                        help='force removal even if content is not on a '
                        'server (it gets recorded in the backlog as if it is, '
                        'and still will still fail if server does not exist)')
    args = parser.parse_args()

    validate_servers(args.servers)

    if cn.interm:
        if not args.cids:
            parser.print_help()
            cn.quit(1)
        src = args.cids
    else:
        src = cn.readpipe()

    for cid in src:
        if remove_from_servers(cid, args.servers, args.force):
            cn.pstd(cn.color.yellow('{}: WARN'.format(cid)))
        else:
            cn.pstd(cn.color.green('{}: OK'.format(cid)))


if __name__ == '__main__':
    main()
