#!/usr/bin/env python

"""
Reformat JSON metadata

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import json


VALID_KEYS = (
    # Required
    'title',
    'url',
    'timestamp',
    'broadcast',
    'license',
    # Optional
    'images',
    'language',
    'multipage',
    'index',
    'keywords',
    'archive',
    'partner',
    'publisher',
    'is_partner',
    'is_sponsored',
    'keep_formatting',
)

DEFAULT_FLAGS = {
    'archive': 'core',
    'images': 0,
    'index': 'index.html',
    'is_partner': False,
    'is_sponsored': False,
    'keep_formatting': False,
    'keywords': '',
    'language': '',
    'multipage': False,
    'partner': '',
    'publisher': '',
}


def cleanmeta(data):
    """ Ensures that legacy metadata is up to date with current standard """
    data['broadcast'] = '$BROADCAST'
    data['publisher'] = None

    if 'partner' in data:
        # Note: Specs currently allow both keys to exist as long as they have
        # the exact same value. We comforming to this allowance until specs
        # explicitly remove the partner key.
        data['publisher'] = data['partner']

    keys = list(data.keys())  # stash keys because keys will be deleted
    for k in keys:
        if k not in VALID_KEYS:
            del data[k]

    # Add default flags so metadata is easier to edit
    for k, v in DEFAULT_FLAGS.items():
        if data.get(k) is None:
            # Previously, default values for some keys were not strictly
            # defined, and some keys simply defalted to ``null``. We are
            # setting the correct default value as per the specs.
            data[k] = v
        data.setdefault(k, v)


def reformat(path):
    """ Reformats the JSON data and overwrites the file

    During reformatting, a placeholder is added for broadcast timestamp.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    cleanmeta(data)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    import os
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Reformat JSON metadata')
    parser.add_argument('path', metavar='PATH', help='JSON file or content '
                        'directory (dfaults to info.json in current '
                        'directory, ignored when used in a pipe)',
                        default='./info.json', nargs='?')
    args = parser.parse_args()

    def doreformat(path):
        path = path.strip()
        if not os.path.basename(path) == 'info.json':
            infopath = os.path.join(path, 'info.json')
        else:
            infopath = path
        reformat(infopath)
        print(path)

    if os.isatty(0):
        doreformat(args.path)
    else:
        path = sys.stdin.readline()
        while path:
            doreformat(path)
            path = sys.stdin.readline()
