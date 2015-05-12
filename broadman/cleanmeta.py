#!/usr/bin/env python

"""
Reformat JSON metadata

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import conz

import outernet_metadata.values as values

from . import jsonf


cn = conz.Console()


BOOL_KEYS = [k for k, v in values.DEFAULTS.items() if v is False]


def cleanmeta(data):
    """ Ensures that legacy metadata is up to date with current standard """
    # Remove all keys that are not in the specs
    datakeys = list(data.keys())
    for k in datakeys:
        if k not in values.KEYS:
            del data[k]

    # Set default broadcast placeholder if broadcast key is missing
    if 'broadcast' not in data:
        data['broadcast'] = '$BROADCAST'

    # Copy partner to publisher
    if 'partner' in data and 'publisher' not in data:
        data['publisher'] = data['partner']

    # Copy publisher to partner when publsiher is present
    if 'publisher' in data:
        # This step may seem redundant with the previous one, but it also
        # applies when the previous one does not.
        data['partner'] = data['publisher']

    # Add default flags so metadata is easier to edit
    for k, v in values.DEFAULTS.items():
        if data.get(k) is None:
            # Previously, default values for some keys were not strictly
            # defined, and some keys simply defalted to ``null``. We are
            # setting the correct default value as per the specs. We are also
            # adding any missing default keys to make editing by humans easier.
            data[k] = v

    # We finally need to find any keys that are using 0 and 1 for boolean
    # values
    for k in BOOL_KEYS:
        if type(data[k]) is int:
            data[k] = bool(data[k])


def reformat(p):
    """ Reformats the JSON data and overwrites the file

    During reformatting, a placeholder is added for broadcast timestamp.
    """
    data = jsonf.load(p)
    cleanmeta(data)
    jsonf.save(p, data)


def main():
    import os
    from . import path
    from . import args

    parser = args.getparser(
        'Reformat JSON metadata',
        usage='%(prog)s CID [CID...]\n     CID | %(prog)s')
    parser.add_argument('cids', metavar='CID', nargs='*',
                        help='content ID, content directory, or path to '
                        'metadata file')
    args = parser.parse_args()

    if cn.interm:
        if not args.cids:
            parser.print_help()
            cn.quit(1)
        src = args.cids
    else:
        src = cn.readpipe()

    for cid in src:
        if os.path.basename(cid) == 'info.json':
            p = cid
        else:
            p = path.infopath(path.contentdir(path.cid(cid)))
        try:
            reformat(p)
            cn.pok(cid)
        except jsonf.LoadError:
            cn.png(cid)


if __name__ == '__main__':
    main()
