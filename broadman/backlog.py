""""
Funcions for managing the backlog

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import os
import datetime
import fileinput

from . import git
from . import path


TSFMT = '%Y-%m-%dT%H:%M:%S%z'


def format_backlog(action, cid, server):
    """ Format the backlog message for given action and content ID """
    user = git.git('config', 'user.email').strip()
    if not user:
        raise RuntimeError('Git user has no email, cannot modify backlog')
    return ' '.join([action, cid, server, user,
                     datetime.datetime.now().strftime(TSFMT)])


def rem_cid(cid, server):
    """ Remove entries that match the given content ID """
    if not os.path.exists(path.BACKLOG):
        return
    for l in fileinput.input(path.BACKLOG, inplace=True):
        if l.strip() == '':
            continue
        lsp = l.split(' ')
        if lsp[1] == cid and lsp[2] == server:
            continue
        print(l, end='')  # Note that with inplace argument, STDOUT is the file


def write_backlog(msg):
    """ Write a backglog entry """
    with open(path.BACKLOG, 'a+') as f:
        f.write(msg + '\n')


def cadd(cid, server):
    msg = format_backlog('ADD', cid, server)
    rem_cid(cid, server)
    write_backlog(msg)


def cdel(cid, server):
    msg = format_backlog('DEL', cid, server)
    rem_cid(cid, server)
    write_backlog(msg)
