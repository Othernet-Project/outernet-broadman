#!/usr/bin/env python

"""
Match inside JSON data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import json


def match(path, key, keyword, match_case=False):
    """ Return True if keyword is found within a key of JSON file at path """
    with open(path, 'r') as f:
        data = json.load(f, encoding='utf8')
    val = str(data.get(key, ''))
    if not match_case:
        keyword = keyword.lower()
        val = val.lower()
    return keyword in val


if __name__ == '__main__':
    import os
    import sys
    import argparse

    parser = argparse.ArgumentParser('Match within JSON key values')
    parser.add_argument('keyword', metavar='KEYWORD', help='search keyword')
    parser.add_argument('key', metavar='KEY', help='key within the JSON data')
    parser.add_argument('-m', action='store_true', help='match case')
    args = parser.parse_args(sys.argv[1:])

    if os.isatty(0):
        print('Type one path per line and press Ctrl-D to process them')

    path = sys.stdin.readline()
    while path:
        if match(path.strip(), args.key, args.keyword, args.m):
            print(path)
        path = sys.stdin.readline()
