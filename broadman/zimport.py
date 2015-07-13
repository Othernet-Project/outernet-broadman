#!/usr/bin/python

"""
Import content from existing content zipball

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys
import shutil
import tempfile

from git.exc import GitCommandError

import conz
from outernet_metadata import values
from outernet_metadata import validator

from . import git
from . import path
from . import zips
from . import jsonf
from . import editor


cn = conz.Console()


def update_metadata(p):
    # Load the metadata
    try:
        data = jsonf.load(p)
    except jsonf.LoadError:
        raise ValueError(None)
    # Update the metadta with defaults
    data.update(values.DEFAULTS)
    data.update({'broadcast': '$BROADCAST'})
    # Check for keys that are not in the specs
    dkeys = list(data.keys())
    for k in dkeys:
        if k not in values.REQUIRED and k not in values.OPTIONAL:
            del data[k]
    jsonf.save(p, data)


def ask_edit(p, errors):
    ans = cn.yesno('Fix metadata?', default=True)
    if not ans:
        raise ValueError(errors)
    editor.edit(p)


def check_metadata(p, interactive=False):
    data = jsonf.load(p)
    errors = validator.validate(data)
    if not errors:
        return
    if errors and not interactive:
        raise ValueError(errors)
    for k, v in errors.items():
        cn.pverr(cn.color.red(k), v.args[0])
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
    cn.pverb('Importing from {}'.format(p))
    tmpdir = tempfile.mkdtemp()
    hash = zips.zcid(p)
    infpath = os.path.join(tmpdir, hash, 'info.json')
    target_path = path.contentdir(hash)
    warnings = False
    try:
        with cn.progress('Preparing target directory') as prg:
            try:
                prep_target(target_path)
            except RuntimeError:
                prg.abrt(post=lambda: cn.perr('Target already exists'))
        with cn.progress('Checking zip file', 'Invalid zip file: {err}'):
            zips.check(p)
        with cn.progress('Unpacking zip content', 'Invalid zip file: {err}'):
            zips.unzip(p, tmpdir)
        with cn.progress('Updating metadata', 'Invalid metadata file'):
            update_metadata(infpath)
        with cn.progress('Checking metadata', 'Invalid metadata'):
            try:
                check_metadata(infpath, cn.verbose)
            except ValueError:
                warnings = True
                cn.perr('{} invalid metadata data'.format(hash))
        with cn.progress('Copying files'):
            shutil.copytree(os.path.join(tmpdir, hash), target_path)
        with cn.progress('Cleaning up'):
            shutil.rmtree(tmpdir)
        with cn.progress('Committing changes', excs=(GitCommandError,)):
            git.commit_import(target_path)
        if warnings:
            cn.pstd(cn.color.yellow('{} WARN'.format(p)))
        else:
            cn.pstd(cn.color.green('{} OK'.format(p)))
    except cn.ProgressAbrt:
        cn.pstd(cn.color.red('{} ERR'.format(p)))
        shutil.rmtree(tmpdir)
        if cn.verbose:
            sys.exit(1)


def main():
    from . import args

    parser = args.getparser(
        'Import existing content zipball into content pool',
        usage='%(prog)s [-h] [-V] [-v] PATH\n'
        '       PATH | %(prog)s [-h] [-V]',
        has_debug=True)

    parser.add_argument('path', metavar='PATH', nargs='?',
                        help='path to zipball')
    args = parser.parse_args()

    if args.debug:
        cn.debug = True

    if sys.stdin.isatty():
        cn.verbose = True
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
