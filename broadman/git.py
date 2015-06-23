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
    def __init__(self, stdout, cmd):
        cmd = ' '.join(cmd)
        self.stdout = stdout
        self.cmd = cmd
        msg = "Git error while running '{}': {}".format(cmd, stdout)
        super(GitError, self).__init__(msg)


def git(*cmd, **kwargs):
    cmd = ('git',) + cmd
    p = subprocess.Popen(cmd, cwd=path.POOLDIR, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise GitError(stderr.decode(sys.stderr.encoding), cmd)
    return stdout.decode(sys.stdout.encoding)


def has_changes(p):
    """ Check whether some path contains changes """
    return git('status', '-s', p)


def get_history(p):
    """ Get all commit hashes for a given path as a list """
    hashes = git('log', '--pretty=format:%H', p)
    return hashes.split('\n')


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
    if not cid:
        cid = 'BACKLOG'
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


def commit_update(p):
    has_history = len(get_history(p)) > 0
    git('add', p)
    changes = has_changes(p)
    if has_history:
        msg = 'Files changed:\n\n{}'.format(changes)
        action = 'UPD'
    else:
        msg = 'Files added:\n\n{}'.format(changes)
        action = 'NEW'
    commit(p, action, msg=msg, noadd=True)


def commit_backlog(processed):
    msg = 'Backlog processed:\n\n{}'.format('\n'.join(processed))
    commit(path.BROADCAST, action='BKL', msg=msg)


def revert(p):
    """ Revert given path to specified hash """
    history = get_history(p)
    if len(history) < 2:
        raise ValueError('nothing to do')
    git('checkout', history[1], p)
    msg = 'Reverted {} to previous state'.format(history[1])
    commit(p, 'REV', msg=msg)


def reset(p):
    """ Remove any changes on path """
    history = get_history(p)
    if len(history) < 1:
        raise ValueError('nothing to do')
    git('clean', '-fd', p)
    git('checkout', history[0], p)


def remove(p):
    """ Remove directory and all contents """
    git('rm', '-rf', p)
    msg = 'Removed {} from pool'.format(p)
    commit(p, 'REM', msg=msg, noadd=True)
