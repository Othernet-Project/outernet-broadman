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
import outernet_metadata.validate as validate
import outernet_metadata.values as values

from . import git
from . import path
from . import jsonf


IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']


cn = conz.Console()


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


def add_optional_keys(data):
    for k, v in values.DEFAULTS.items():
        if k not in data:
            data[k] = v
    if 'broadcast' not in data:
        data['broadcast'] = '$BROADCAST'


def update_image_count(p, data):
    matcher = lambda p: os.path.splitext(p)[1].lower() in IMAGE_EXTS
    data['images'] = path.countwalk(p, matcher)
    assert data['images'] >= 0, 'Expected image count to be 0 or more'


def update(cid, add_optional=False, update_images=False, reformat=False):
    cdir = path.contentdir(cid)
    infopath = path.infopath(cdir)
    if not git.has_changes(cdir):
        cn.pverr(cid, 'nothing to update')
        return
    try:
        data = jsonf.load(infopath)
    except jsonf.LoadError:
        raise ValueError('invalid metadata file')
    # Modify data if needed
    if add_optional:
        add_optional_keys(data)
    if update_images:
        update_image_count(data)
    if any([add_optional, update_images, reformat]):
        jsonf.save(infopath, data)
    # Validate metadata
    ret = validate.validate(data)
    if ret:
        getter = lambda k, o: (cid, '{} - {}'.format(k, o[k].args[0]))
        cn.poerr(ret, key=getter)
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
    revopt.add_argument('--reset', '-R', action='store_true',
                        help='reset all changes instead of updating (cannot '
                        'be used with --revert)')
    revopt.add_argument('--revert', '-v', action='store_true',
                        help='revert last set of changes (cannot be used with '
                        'reset)')
    metagrp = parser.add_argument_group('Metadata options (ignored '
                                        'when --reset or --revert are used)')
    metagrp.add_argument('--add-optional', '-a', action='store_true',
                         help='add all misssing optional keys')
    metagrp.add_argument('--update-images', '-i', action='store_true',
                         help='update image count based on actual content')
    metagrp.add_argument('--reformat', '-r', action='store_true',
                         help='reformat the metadata file')
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
    else:
        fn = lambda cid: update(cid, add_optional=args.add_optional,
                                update_images=args.update_images,
                                reformat=args.reformat)

    for cid in src:
        cid = path.cid(cid.strip())
        try:
            fn(cid)
            cn.pok(cid)
        except ValueError:
            cn.png(cid)


if __name__ == '__main__':
    main()
