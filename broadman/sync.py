#!/usr/bin/python

"""
Sync to appropriate server

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

Syncdefs
========

This tool relies on syncdefs, which are text files named ``.syncdef``,
located in the root of a server directory. This script will exit with an error
message if it cannot locate the syncdef file.

The file should contain two lines. Both lines are commands lines. The first
line is used to add content to a server, and another is used to remove the file
from the server.

Each of the commands may have optional placeholders:

- ``%(path)s`` - absolute path to content directory
- ``%(zip)s`` - absolute path to packaged zip file
- ``%(cid)s`` - content ID

The path and zip placeholders are only used for add syncdef, and the cid is
passed to both.

Remaining lines in the file can be used for any purpose are are not read by
this script.
"""

import os
import json
import shlex
import tempfile
import datetime
import subprocess
import contextlib

import conz

from . import db
from . import git
from . import path
from . import zips
from . import jsonf


try:
    FILE_ERRORS = (IOError, OSError, FileNotFoundError)
except NameError:
    FILE_ERRORS = (IOError, OSError)


DTFMT = '%Y-%m-%d %H:%M:%S UTC'

cn = conz.Console()


def broadcast_date():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d')


def add_broadcast_date(data):
    """ Modify JSON data and add broadcast datestamp """
    data = json.loads(data.decode('utf8'))
    data['broadcast'] = broadcast_date()
    return json.dumps(data, indent=4, sort_keys=True).encode('utf8')


def read_syncdef(srv):
    srvdir = path.serverdir(srv)
    sdpath = os.path.join(srvdir, '.syncdef')
    defs = {}
    with open(sdpath, 'r') as f:
        defs['add'] = f.readline().strip()
        defs['del'] = f.readline().strip()
    return defs


@contextlib.contextmanager
def patched_info(infopath):
    # We use a context manager to patch the metadata because zipfile module
    # does not support modifying contents in-place, and in many cases we cannot
    # afford to copy contents (e.g., content that's multiple gigabytes).
    data_orig = jsonf.load(infopath)
    data = data_orig.copy()
    data['broadcast'] = broadcast_date()
    jsonf.save(infopath, data)
    yield
    jsonf.save(infopath, data_orig)


def pack_content(cid):
    cdir = path.contentdir(cid)
    tdir = tempfile.mkdtemp()
    infopath = os.path.join(cdir, 'info.json')

    # Pack content
    with cn.progress('Packing zip file', excs=FILE_ERRORS + (RuntimeError,)):
        zname = cid + '.zip'
        zpath = os.path.join(tdir, zname)
        with patched_info(infopath):
            zips.pack(zpath, cdir)

    return zpath


def get_metadata(cid):
    cdir = path.contentdir(cid)
    ipath = path.infopath(cdir)
    return jsonf.load(ipath)


def run_syncdef(syncdef, nosyncdef=False):
    with cn.progress('Executing syncdef',
                     excs=(subprocess.CalledProcessError,)) as prg:
        if nosyncdef:
            prg.end('SKIPPED')
            return
        syncdef = shlex.split(syncdef)
        subprocess.check_call(syncdef)


def add_content(cid, srv, user, metadata, nosyncdef=False):
    # Pack the zipball
    zpath = pack_content(cid)
    packed = datetime.datetime.utcnow()

    cdir = path.contentdir(cid)
    syncdef = read_syncdef(srv)['add'] % {
        'cid': cid,
        'zip': os.path.abspath(zpath),
        'path': os.path.abspath(cdir),
    }
    run_syncdef(syncdef, nosyncdef)
    aired = datetime.datetime.utcnow()

    # Get extra metadata for the database
    hash = git.get_history(cdir)[0]
    url = metadata['url']
    title = metadata['title']
    size = os.stat(zpath).st_size
    collected = datetime.datetime.strptime(metadata['timestamp'], DTFMT)

    # Write the data to database
    with cn.progress('Storing broadcast data', excs=[db.OperationalError]):
        d = db.DB()
        d.add_content(id=cid, server=srv, commit=hash, title=title, url=url,
                      size=size, collected=collected, packed=packed,
                      aired=aired, expires=None)

    tdir = os.path.dirname(zpath)
    os.unlink(zpath)
    os.rmdir(tdir)


def remove_content(cid, srv, user, metadata, nosyncdef=False):
    syncdef = read_syncdef(srv)['del'] % {
        'cid': cid
    }
    run_syncdef(syncdef, nosyncdef)
    with cn.progress('Storing broadcast data', excs=[db.OperationalError]):
        d = db.DB()
        d.remove_content(cid)


def get_backlog():
    with open(path.BACKLOG, 'r') as f:
        return f.readlines()


def clear_backlog():
    with open(path.BACKLOG, 'w') as f:
        f.write('')


def syncall(nosyncdef=False):
    backlog = get_backlog()
    if not backlog:
        raise RuntimeError('No backlog')
    finished = []
    for bl in backlog:
        act, cid, srv, user, ts = bl.strip().split(' ')
        metadata = get_metadata(cid)
        if act == 'ADD':
            add_content(cid, srv, user, metadata, nosyncdef)
            finished.append('+ {}'.format(cid))
        elif act == 'DEL':
            remove_content(cid, srv, user, metadata, nosyncdef)
            finished.append('- {}'.format(cid))
    clear_backlog()
    git.commit_backlog(finished)


def main():
    from . import args

    parser = args.getparser('Sync backlog to servers', has_debug=True,
                            has_verbose=True)
    parser.add_argument('--no-sync-to-server', action='store_true',
                        help='do not sync changes to server (USE THIS OPTION '
                        'ONLY FOR TESTING)', dest='nosync')
    args = parser.parse_args()

    cn.verbose = args.verbose
    cn.debug = args.debug

    def fail(msg):
        cn.perr(msg)
        cn.png('backlog sync')
        cn.quit(1)

    try:
        syncall(args.nosync)
        cn.pok('backlog sync')
    except cn.ProgressAbrt:
        cn.png('backlog sync')
    except RuntimeError:
        cn.pok('no backlog', ok='OK')


if __name__ == '__main__':
    main()
