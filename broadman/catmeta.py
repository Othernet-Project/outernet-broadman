#!/usr/bin/python

"""
Load the metadata for a given path and show the formatted content

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import conz

from . import path
from . import jsonf

cn = conz.Console()


def keylist(keys, filter=[]):
    keys = sorted(keys)
    if not filter:
        return keys
    return [k for k in keys if k in filter]


def print_kv(key, val):
    if val is True:
        val = 'yes'
    if val is False:
        val = 'no'
    if val is None:
        val = 'NULL'
    if val is '':
        val = '(empty)'
    cn.pstd('{:>26}: {}'.format(cn.color.color(key, style='bold'), val))


def print_meta(p, filter=[], include_id=False, include_path=False):
    p = path.infopath(p)
    try:
        data = jsonf.load(p)
    except jsonf.LoadError:
        cn.pstd(cn.color.red('{}: {}'.format(p, 'ERR')))
        cn.pverr(p, 'not found or malformed metadata file')
        return
    if include_id:
        cid = path.cid(p)
        print_kv('ID', cid)
    if include_path:
        print_kv('path', p)
    for k in keylist(data.keys(), filter):
        v = data[k]
        print_kv(k, v)


def main():
    from . import args

    parser = args.getparser(
        'Show metadata from given path',
        usage='%(prog)s [options] CID [CID...]\n       '
        'CID | %(prog)s [options]')
    parser.add_argument('cids', metavar='CID', nargs='*',
                        help='path to content directory or metadata file')
    parser.add_argument('--with-id', '-i', action='store_true',
                        help='include content ID as a key')
    parser.add_argument('--with-path', '-p', action='store_true',
                        help='include content directory path as a key')
    parser.add_argument('--separator', '-s', action='store_true',
                        help='print a blank line after data')
    parser.add_argument('--keys', '-k', metavar='KEY', nargs='*',
                        help='display only these keys', default=[])
    args = parser.parse_args()

    if cn.interm:
        if not args.cids:
            parser.print_help()
            cn.quit(1)
        src = args.cids
    else:
        src = cn.readpipe()

    for p in src:
        p = path.contentdir(path.cid(p.strip()))
        print_meta(p.strip(), args.keys, include_id=args.with_id,
                   include_path=args.with_path)
        if args.separator:
            cn.pstd('')
