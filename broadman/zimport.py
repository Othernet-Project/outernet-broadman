#!/usr/bin/python

"""
Import content from existing content zipball

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import os
import sys
import shutil
import tempfile
import subprocess

from outernet_metadata import validate
from outernet_metadata import values

from . import jsonf
from . import path
from . import conz
from . import zips

EDITOR = os.environ.get('EDITOR', 'vi')

pr = conz.Print()


def edit(p):
    subprocess.call([EDITOR, p])


def update_metadata(p):
    # Load the metadata
    try:
        data = jsonf.load(p)
    except jsonf.LoadError:
        raise ValueError(None)
    # Update the metadta with defaults
    data.update(values.DEFAULTS)
    data.update({'broadcast': '$BROADCAST'})
    jsonf.save(p, data)


def ask_edit(p, errors):
    ans = pr.read('Fix metadata? [Y/n]', clean=lambda x: x.lower()[:1])
    if ans == 'n':
        raise ValueError(errors)
    edit(p)


def check_metadata(p, interactive=False):
    data = jsonf.load(p)
    errors = validate.validate(data)
    if not errors:
        return
    if errors and not interactive:
        raise ValueError(errors)
    for k, v in errors.items():
        pr.perr('{}: {}'.format(pr.color.red(k), v))
    ask_edit(p, errors)
    check_metadata(p, interactive)


def prep_target(p):
    if os.path.exists(p):
        raise RuntimeError()
    p = os.path.dirname(p)
    if os.path.exists(p):
        return
    os.makedirs(p)


def copy_files(srcdir, targetdir):
    shutil.copytree(srcdir, targetdir)


def doimport(p, interactive=False):
    pr.pverb('Importing from {}'.format(p))
    tmpdir = tempfile.mkdtemp()
    hash = zips.zcid(p)
    infpath = os.path.join(tmpdir, hash, 'info.json')
    target_path = path.contentdir(hash)
    warnings = False
    try:
        with pr.progress('Preparing target directory') as prg:
            try:
                prep_target(target_path)
            except RuntimeError:
                prg.abrt(post=lambda: pr.perr('Target already exists'))
        with pr.progress('Checking zip file', 'Invalid zip file: {err}'):
            zips.check(p)
        with pr.progress('Unpacking zip content', 'Invalid zip file: {err}'):
            zips.unzip(p, tmpdir)
        with pr.progress('Updating metadata', 'Invalid metadata file'):
            update_metadata(infpath)
        with pr.progress('Checking metadata', 'Invalid metadata'):
            try:
                check_metadata(infpath, pr.verbose)
            except ValueError:
                warnings = True
                pr.perr('{} invalid metadata data'.format(hash))
        with pr.progress('Copying files'):
            shutil.copytree(os.path.join(tmpdir, hash), target_path)
        with pr.progress('Cleaning up'):
            shutil.rmtree(tmpdir)
        if warnings:
            pr.pstd(pr.color.yellow('{} WARN'.format(p)))
        else:
            pr.pstd(pr.color.green('{} OK'.format(p)))
    except pr.ProgressAbrt:
        pr.pstd(pr.color.red('{} ERR'.format(p)))
        shutil.rmtree(tmpdir)
        if pr.verbose:
            sys.exit(1)


def main():
    from . import args

    parser = args.getparser(
        'Import existing content zipball into content pool',
        usage='%(prog)s [-h] [-V] [-v] PATH\n'
        '       PATH | %(prog)s [-h] [-V]')

    parser.add_argument('path', metavar='PATH', nargs='?',
                        help='path to zipball')
    args = parser.parse_args()

    if sys.stdin.isatty():
        pr.verbose = True
        if not args.path:
            parser.print_help()
            sys.exit(0)
        doimport(args.path)
    else:
        p = sys.stdin.readline()
        while p:
            doimport(p.strip())
            p = sys.stdin.readline()


if __name__ == '__main__':
    main()
