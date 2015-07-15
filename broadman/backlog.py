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
    user = git.Git().git.config('user.email').strip()
    if not user:
        raise RuntimeError('Git user has no email, cannot modify backlog')
    return ' '.join([action, cid, server, user,
                     datetime.datetime.now().strftime(TSFMT)])


def match_line(cid, server, l):
    """ Checks a single backlog line if it matches cid-server combination

    Returns the line split into parts.
    """
    lsp = l.split(' ')
    if not lsp:
        return None
    if lsp[1] == cid and lsp[2] == server:
        return lsp


def rem_cid(cid, server):
    """ Remove entries that match the given content ID """
    if not os.path.exists(path.BACKLOG):
        return
    for l in fileinput.input(path.BACKLOG, inplace=True):
        if l.strip() == '':
            continue
        if match_line(cid, server, l):
            continue
        print(l, end='')  # Note that with inplace argument, STDOUT is the file


def has_cid(cid, server):
    """ Checks wether cid-server combination is in backlog """
    with open(path.BACKLOG) as f:
        for l in f:
            ret = match_line(cid, server, l)
            if not ret:
                continue
            return ret


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
    ret = has_cid(cid, server)
    if not ret:
        write_backlog(msg)
        return
    if ret[0] == 'ADD':
        # Just rever the add
        rem_cid(cid, server)
    # Probably already deleted
