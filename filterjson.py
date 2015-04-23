#!/usr/bin/env python

"""
Match inside JSON data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import sys
import json
from datetime import datetime


DATEFMT = '%Y-%m-%d'
TSFMT = '%Y-%m-%d %H:%M:%S'


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def vfail(value, msg):
    fail('{}: {}'.format(value, msg))


def parse_date(s):
    try:
        return datetime.strptime(s, DATEFMT)
    except ValueError:
        vfail(s, 'not a valid date')

def parse_ts(s):
    try:
        return datetime.strptime(s, TSFMT)
    except ValueError:
        vfail(s, 'not a valid timestamp')


def parse_num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        vfail(s, 'not a numeric value')


def parse_bool(s):
    return s.lower() not in ['no', 'false', 'null', '0']


def prep_kw(s, vtype=None):
    if not vtype:
        return s
    if vtype == 'd':
        return parse_date(s)
    if vtype == 't':
        return parse_ts(s)
    if vtype == 'n':
        return parse_num(s)
    if vtype == 'b':
        return parse_bool(s)
    vfail(vtype, 'not a supported type')


def match(path, key, keyword, xmatch=False, icase=True, gt=False, lt=False):
    """ Return True if keyword is found within a key of JSON file at path """
    try:
        with open(path, 'r') as f:
            data = json.load(f, encoding='utf8')
    except FileNotFoundError:
        vfail(path, 'file not found')
    except ValueError:
        vfail(path, 'could not parse metadata')

    val = data.get(key, '')

    if icase:
        val = str(val).lower()
        keyword = str(keyword).lower()

    if isinstance(keyword, datetime):
        val = parse_ts(val.rstrip(' UTC'))

    if xmatch or keyword in [True, False]:
        print('xmatching')
        return keyword == val

    if gt:
        return val > keyword

    if lt:
        return val < keyword

    return keyword in val


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(
        description='Match within JSON key values')
    parser.add_argument('keyword', metavar='KEYWORD', help='search keyword')
    parser.add_argument('key', metavar='KEY', help='key within the JSON data')
    parser.add_argument('path', metavar='PATH', help='JSON file (dfaults to '
                        'info.json in current directory, ignored when used in '
                        'a pipe)', default='./info.json', nargs='?')

    # Match type
    parser.add_argument('-x', action='store_true',
                        help='exact match', default=False)
    parser.add_argument('-i', action='store_true',
                        help='ignore case', default=False)
    parser.add_argument('-gt', action='store_true',
                        help='do a greater-than KEYWORD match', default=False)
    parser.add_argument('-lt', action='store_true',
                        help='do a less-than KEYWORD match', default=False)

    # Value type
    parser.add_argument('-t', help='treat KEYWORD as type (d for date in '
                        'YYYY-MM-DD format, t for timestamp in YYYY-MM-DD '
                        'HH:MM:SS format, n for numeric, b for boolean)',
                        metavar='TYPE', default=None)

    args = parser.parse_args(sys.argv[1:])

    if os.isatty(0):
        path = args.path
        kw = prep_kw(args.keyword, args.t)
        if match(path.strip(), args.key, kw, args.x, args.i, args.gt, args.lt):
            print(path)
    else:
        path = sys.stdin.readline()
        while path:
            kw = prep_kw(args.keyword, args.t)
            if match(path.strip(), args.key, kw, args.x, args.i, args.gt,
                     args.lt):
                print(path)
            path = sys.stdin.readline()
