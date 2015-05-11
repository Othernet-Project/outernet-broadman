"""
Git wrapper functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys
import subprocess

from . import path
from . import __version__


MSG_MARKER = '[OBM]'


class GitError(Exception):
    def __init__(self, stdout):
        self.stdout = stdout
        super(GitError, self).__init__(stdout)


def git(*cmd, **kwargs):
    cmd = ('git',) + cmd
    p = subprocess.Popen(cmd, cwd=path.POOLDIR, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        raise GitError(p.stderr.read().decode(sys.stderr.encoding))
    return p.stdout.read().decode(sys.stdout.encoding)


def init():
    git('init')
    vfile = os.path.join(path.POOLDIR, '.version')
    with open(vfile, 'w') as f:
        f.write(__version__ + '\n')
    git('add', vfile)
    git('commit', '--author', 'Outernet Broadman <apps@outernet.is>', '-m',
        'Initialized content pool')


def commit(p, action, msg=None, extra_data=[], noadd=False):
    if not noadd:
        git('add', p)
    cid = path.cid(p)
    cmsg = [MSG_MARKER, action, cid]
    cmsg.extend(extra_data)
    cmsg = ' '.join(cmsg)
    if msg:
        cmsg += '\n\n' + msg
    git('commit', '-m', cmsg)


def commit_import(p):
    commit(p, action='IMP', msg='Imported new content')


def commit_add_to_server(p, server):
    cid = path.cid(p)
    msg = 'Added {} -> {}'.format(cid, server)
    commit(p, action='ADD', msg=msg, extra_data=[server])


def commit_remove_from_server(p, server):
    git('rm', '--cached', p)
    cid = path.cid(p)
    msg = 'Removed {} <- {}'.format(cid, server)
    commit(p, action='DEL', msg=msg, extra_data=[server], noadd=True)
