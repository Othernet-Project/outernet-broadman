"""
Git wrapper functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
from os.path import abspath

from git import Repo, Actor

from . import path
from . import __version__


MSG_MARKER = '[OBM]'
AUTHOR = Actor("Outernet Broadman", "apps@outernet.is")


def init():
    p = path.POOLDIR
    git = Repo.init(p)
    vfile = os.path.join(p, '.version')
    with open(vfile, 'w') as f:
        f.write(__version__ + '\n')
    git.index.add([vfile])
    git.index.commit('Initialized content pool', author=AUTHOR)


class Git():
    def __init__(self):
        repo = Repo(abspath(path.POOLDIR))
        index = repo.index
        self.add = index.add
        self.git = repo.git
        self.commit = index.commit
        self.remove = index.remove

    def has_changes(self, p):
        """ Check whether some path contains changes """
        return self.git.status(p, s=True)

    def get_history(self, p):
        """ Get all commit hashes for a given path as a list """
        hashes = self.git.log(pretty='format:%H')
        return hashes.split('\n')

    def commit(self, p, action, msg=None, extra_data=[], noadd=False):
        if not noadd:
            self.add(p)
        cid = path.cid(p)
        if not cid:
            cid = 'BACKLOG'
        cmsg = [MSG_MARKER, action, cid]
        cmsg.extend(extra_data)
        cmsg = ' '.join(cmsg)
        if msg:
            cmsg += '\n\n' + msg
        self.commit(cmsg)

    def commit_import(self, p):
        self.commit(p, action='IMP', msg='Imported new content')

    def commit_add_to_server(self, p, server):
        cid = path.cid(p)
        msg = 'Added {} -> {}'.format(cid, server)
        self.commit(p, action='ADD', msg=msg, extra_data=[server])

    def commit_remove_from_server(self, p, server):
        self.remove([p], cached=True)
        cid = path.cid(p)
        msg = 'Removed {} <- {}'.format(cid, server)
        self.commit(p, action='DEL', msg=msg, extra_data=[server], noadd=True)

    def commit_update(self, p):
        has_history = len(self.get_history(p)) > 0
        self.add(p)
        changes = self.has_changes(p)
        if has_history:
            msg = 'Files changed:\n\n{}'.format(changes)
            action = 'UPD'
        else:
            msg = 'Files added:\n\n{}'.format(changes)
            action = 'NEW'
        self.commit(p, action, msg=msg, noadd=True)

    def commit_backlog(self, processed):
        msg = 'Backlog processed:\n\n{}'.format('\n'.join(processed))
        self.commit(path.BROADCAST, action='BKL', msg=msg)

    def revert(self, p):
        """ Revert given path to specified hash """
        history = self.get_history(p)
        print(history)
        print(history[1])
        if len(history) < 2:
            raise ValueError('nothing to do')
        self.git.checkout(history[1], p=True)
        msg = 'Reverted {} to previous state'.format(history[1])
        self.commit(p, 'REV', msg=msg)

    def reset(self, p):
        """ Remove any changes on path """
        history = self.get_history(p)
        if len(history) < 1:
            raise ValueError('nothing to do')
        self.git.clean(f=True, d=True, p=True)
        self.git.checkout(history[0], p=True)

    def remove(self, p):
        """ Remove directory and all contents """
        self.remove([p])
        msg = 'Removed {} from pool'.format(p)
        self.commit(p, 'REM', msg)
