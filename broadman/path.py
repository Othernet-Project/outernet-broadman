"""
Functions for working with paths

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import division

import os

# Definitive rule for where to get the content pool directory
POOLDIR = os.environ.get('OUTERNET_CONTENT', '.').rstrip(os.sep)

# Default content ID length
CIDLEN = 32

# Default path segment length
SEGLEN = 3

# Characters allowd in paths
PATHCHARS = '[0-9a-f]'


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

    try:
        names = os.listdir(path)
    except OSError:
        return

    for name in names:
        for child in fnwalk(os.path.join(path, name), fn, shallow):
            yield child


def splitseg(s, l=SEGLEN):
    """ Split the string into segments of given length. """
    while s:
        yield s[:l]
        s = s[l:]


def segrx(s, l=SEGLEN):
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


def pathrx(cid, l=SEGLEN):
    """
    Return a regex pattern that matches content path for content ID.

    `cid`` can be either a full or a partial content ID. Using full content ID
    returns a pattern that is equivalent of simply segmenting the path using
    ``splitseg()`` and joining with the default path separator.
    """
    if len(cid) == CIDLEN:
        # This is a special case where we got a full CID, so there's no regular
        # expressions to create
        return os.sep.join(splitseg(cid, l))
    ltail = CIDLEN % l
    lhead = CIDLEN - ltail
    totsegs = CIDLEN // l
    # Split the CID into head and tail portions
    head = cid[:lhead]
    tail = cid[lhead:]
    # Convert head to segments
    segs = [segrx(s, l) for s in splitseg(head, l)]
    nsegs = len(segs)
    if not nsegs:
        segs.append(segrx('', l))
        nsegs = 1
    fullseg_missing = totsegs - nsegs
    # Construct the regex
    rx = os.sep.join(segs)
    if fullseg_missing:
        # Addd any missing full segments
        rx += '(?:/%s){%s}' % (segrx('', l), fullseg_missing)
    if ltail:
        # Attach the tail
        rx += '/{}'.format(segrx(tail, ltail))
    return rx


def contentdir(cid, l=SEGLEN):
    """
    Return a content directory matching content id regardless of whether it
    exists
    """
    return os.path.join(POOLDIR, os.sep.join(splitseg(cid, l)))
