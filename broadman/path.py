"""
Functions for working with paths

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import division

import re
import os
import scandir


try:
    FILE_ERRORS = (IOError, OSError, FileNotFoundError)
except NameError:
    FILE_ERRORS = (IOError, OSError)

try:
    DIR_ERRORS = (OSError, NotADirectoryError)
except NameError:
    DIR_ERRORS = (OSError,)


# Definitive rule for where to get the content pool directory
POOLDIR = os.environ.get('OUTERNET_CONTENT', '.').rstrip(os.sep)

# Path to backlog file
BACKLOG = os.path.join(POOLDIR, '.backlog')

# Broad cast log database
BROADCAST = os.path.join(POOLDIR, 'broadcast.sqlite')

# Default content ID length
CIDLEN = 32

# Characters allowd in paths
PATHCHARS = '[0-9a-f]'

# Regexp to match content ID
CIDRE = re.compile('%(pc)s{%(len)s}' % {'pc': PATHCHARS, 'len': CIDLEN})

# Default server directory
DEFAULT_SERVER = 'master'


def fnwalk(path, fn, shallow=False):
    """
    Walk directory tree top-down until directories of desired length are found

    This generator function takes a ``path`` from which to begin the traversal,
    and a ``fn`` object that selects the paths to be returned. It calls
    ``os.listdir()`` recursively until either a full path is flagged by ``fn``
    function as valid (by returning a truthy value) or ``os.listdir()`` fails
    with ``OSError``.

    This function has been added specifically to deal with large and deep
    directory trees, and it's tehrefore not avisable to convert the return
    values to a lists and similar memory-intensive objects.

    The ``shallow`` flag is used to terminate further recursion on match. If
    ``shallow`` is ``False``, recursion continues even after a path is matched.

    For example, given a path ``/foo/bar/bar``, and a matcher that matches
    ``bar``, with ``shallow`` flag set to ``True``, only ``/foo/bar`` is
    matched. Otherwise, both ``/foo/bar`` and ``/foo/bar/bar`` are matched.
    """
    if fn(path):
        yield path
        if shallow:
            return

    entries = scandir.scandir(path)

    try:
        for entry in entries:
            for child in fnwalk(entry.path, fn, shallow):
                yield child
    except OSError:
        return


def countwalk(path, fn):
    """
    Walk directory tree top-down and count files that match the function.

    The matcher function, ``fn``, must return ``True``, ``False``, 1 or 0.

    This function returns an integer count of all matched files.
    """
    count = 0
    for e in scandir.scandir(path):
        if e.is_file():
            count += fn(e.name)
        else:
            count += countwalk(e.path, fn)
    return count


def cidrx(s, l=CIDLEN):
    """
    Return a pattern that matches full or partial path segment of given length
    """
    if l <= 0:
        return ''
    s = s[:l]
    lens = len(s)
    if lens == l:
        return s
    return s + '%s{%s}' % (PATHCHARS, l - lens)


def serverdir(server=DEFAULT_SERVER):
    """
    Return server directory.
    """
    return os.path.join(POOLDIR, server)


def contentdir(cid, server=DEFAULT_SERVER):
    """
    Return a content directory matching content id regardless of whether it
    exists
    """
    return os.path.join(serverdir(server), cid)


def cid(s):
    """
    Extract content ID from given string.
    """
    m = CIDRE.search(s)
    if not m:
        return None
    return s[m.start():m.end()]


def find_contentdirs(cids, server=DEFAULT_SERVER):
    if not cids:
        cidsrx = cidrx('')
    else:
        cidsrx = '|'.join(cidrx(cid) for cid in cids)
    cidsrx = re.compile(cidsrx)
    sd = serverdir(server)
    try:
        for entry in scandir.scandir(sd):
            if cidsrx.search(entry.name):
                yield entry.path
    except FILE_ERRORS:
        return


def infopath(path):
    """
    Returns path to info.json

    If ``path`` points to content directory, then full path to info.json file
    is returned. If ``path`` already points to info.json, then it is returned
    as is.
    """
    if os.path.basename(path) == 'info.json':
        return path
    return os.path.join(path, 'info.json')
