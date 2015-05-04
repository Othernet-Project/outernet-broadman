#!/usr/bin/python

"""
Simple metadata editor

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from outernet_metadata import validate
from validators import make_chain

from . import conz
from . import data
from . import path
from . import jsonf

cn = conz.Console()

# Map metadata keys to their types
METAKEYS = {
    'title': None,
    'url': None,
    'timestamp': None,
    'broadcast': None,
    'license': None,
    'images': None,
    'language': None,
    'publisher': None,
    'index': None,
    'keywords': None,
    'multipage': 'b',
    'is_partner': 'b',
    'is_sponsored': 'b',
    'keep_formatting': 'b'
}

IMGEXT = ['.jpg', '.jpeg', '.png', '.gif', '.svg']


def isimg(p):
    return os.path.splitext(p)[1].lower() in IMGEXT


def clean(key, val):
    """ Coerce value to appropriate type """
    return data.totype(val, METAKEYS[key])


def check(key, val):
    chain = make_chain(validate.values.SPECS[key])
    return chain(val)


def convert_args(args):
    """ Convert values supplied thorugh args to Python values

    If data format errors are encountered, the program is terminated and errors
    are printed to STDERR.
    """
    data = {}
    errors = {}
    for k in METAKEYS:
        v = getattr(args, k)
        if v is None:
            continue
        try:
            v = clean(k, v)
            data[k] = v
        except ValueError as err:
            errors[k] = err.args[0]
    if errors:
        for k, v in errors.items():
            cn.pverr(cn.color.red(k), v)
        cn.quit(1)
    return data


def check_args(data):
    """ Validate all values against authoritative schema

    If validation errors occur, the program writes the invalid keys to STDOUT
    and quits.
    """
    errors = {}
    for k, v in data.items():
        try:
            check(k, v)
        except ValueError as err:
            if k == 'images':
                # images are special-case, because the default validator will
                # not allow negative values, but in this case we do allow them
                # and handle them later to obtain correct count from files in
                # the content directory.
                continue
            errors[k] = err.args[0]
    if errors:
        for k, v in errors.items():
            cn.pverr(cn.color.red(k), v)
        cn.quit(1)
    return data


def count_imgs(p):
    if p.endswith('info.json'):
        p = os.path.dirname(p)
    return path.countwalk(p, isimg)


def set_vals(p, data):
    if not p.endswith('info.json'):
        p = os.path.join(p, 'info.json')
    meta = jsonf.load(p)
    if 'images' in data and data['images'] < 0:
        data['images'] = count_imgs(p)
        assert data['images'] >= 0, 'Expected positive image count'
    meta.update(data)
    jsonf.save(p, meta)


def main():
    from . import args

    parser = args.getparser('Set metadata keys',
                            usage='%(prog)s [options] PATH\n       '
                            'PATH | %(prog)s [options]')

    parser.add_argument('paths', metavar='PATH', nargs='*',
                        help='path to metadata file or content directory '
                        '(ignored when used in a pipe)')
    parser.add_argument('--title', '-t', metavar='TITLE', help='set title')
    parser.add_argument('--url', '-u', metavar='URL', help='set URL')
    parser.add_argument('--timestamp', '-s', metavar='TIMESTAMP',
                        help='set creation date in YYYY-MM-DD HH:MM:SS UTC'
                        'format')
    parser.add_argument('--broadcast', '-b', metavar='DATESTAMP',
                        help='set broadcast date in YYYY-MM-DD format')
    parser.add_argument('--license', '-l', metavar='LICENSE_CODE',
                        help='set license code')
    parser.add_argument('--images', metavar='N', type=int,
                        help='set number of images (use negative value such '
                        'as -1 to recalculate from the content directory')
    parser.add_argument('--language', metavar='LC',
                        help='set language locale code')
    parser.add_argument('--publisher', metavar='NAME',
                        help='set publisher name')
    parser.add_argument('--index', metavar='PATH',
                        help='set index (path will be verified)')
    parser.add_argument('--keywords', metavar='KEY,WORDS',
                        help='set comma-separated keywords')
    parser.add_argument('--multipage', choices=['yes', 'no'],
                        help='set multipage flag')
    parser.add_argument('--is_partner', choices=['yes', 'no'],
                        help='set partner flag')
    parser.add_argument('--is_sponsored', choices=['yes', 'no'],
                        help='set sponsored flag')
    parser.add_argument('--keep_formatting', choices=['yes', 'no'],
                        help='set formatting flag')
    parser.add_argument('--delete', '-d', metavar='KEY', nargs='+',
                        help='delete one or more keys')
    args = parser.parse_args()

    data = check_args(convert_args(args))

    if cn.interm:
        if not args.paths:
            parser.print_help()
            cn.quit()
        src = args.paths
    else:
        src = cn.readpipe()

    err = False
    for p in src:
        p = p.strip()
        set_vals(p, data)
        try:
            set_vals(p, data)
            cn.pstd(cn.color.green('{} OK'.format(p)))
        except jsonf.LoadError:
            err = True
            cn.pstd(cn.color.red('{} ERR'.format(p)))
            cn.pverr(p, 'Error loading JSON data')
    if err:
        cn.quit(1)
