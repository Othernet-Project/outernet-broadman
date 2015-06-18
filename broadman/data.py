"""
Functions for working with data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import subprocess
from datetime import datetime

DATEFMT = '%Y-%m-%d'
TSFMT = '%Y-%m-%d %H:%M:%S'

# Type markers
DATESTAMP = 'd'
TIMESTAMP = 't'
NUMERIC = 'n'
BOOLEAN = 'b'


def parse_date(s):
    return datetime.strptime(s, DATEFMT)


def parse_ts(s):
    return datetime.strptime(s, TSFMT)


def parse_num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        ValueError('not a valid numeric value')


def parse_bool(s):
    return s.lower() not in ['no', 'false', 'null', '0']


def totype(s, vtype=None):
    """ Convert string input into value of given type

    The type is specified one of the custom type markes:

    - 'd' - datestamp (YYYY-MM-DD format)
    - 't' - timestamp (YYYY-MM-DD HH:MM:SS format)
    - 'n' - numeric (floats)
    - 'b' - boolean

    If ``vtype`` argument is omitted, value is returned as is.

    If ``vtype`` is an unsupported type, ``ValueError`` is raised.

    If a string cannot be converted, ``ValueError`` is raised.
    """
    if not vtype:
        return s
    if vtype == DATESTAMP:
        return parse_date(s)
    if vtype == TIMESTAMP:
        return parse_ts(s)
    if vtype == NUMERIC:
        return parse_num(s)
    if vtype == BOOLEAN:
        return parse_bool(s)
    raise ValueError('{} is not a supported type'.format(vtype))


def getsize(dir):
    return subprocess.check_output(['du','-s', dir]).split()[0].decode('utf-8')


def sizematch(dir, val, invert=False):
    size = int(getsize(dir))
    return (size > val) ^ invert


def smatch(x, y, xmatch=False, icase=True, **kwargs):
    """ Performs a match against string values """
    if icase:
        x = str(x).lower()
        y = str(y).lower()
    if xmatch:
        return x == y
    return y in x


def nmatch(x, y, gt=False, lt=False, **kwargs):
    """ Perform a match aginst numeric values """
    if lt:
        return x < y
    if gt:
        return x > y
    return x == y


def bmatch(x, y, **kwargs):
    return x is y


def match(data, key, keyword, vtype=None, invert=False, **kwargs):
    """ Performs various matches of keyword against value of a key in data

    ``data`` should be a dict. If there is no key in data, ``None`` is used as
    the value.

    ``keyword`` is a string that is coerced to appropriate type based on the
    value of ``vtype`` using the ``totype()`` function.

    The ``vtype`` value determines the type of match. If no type is passed,
    ``smatch()`` is performed.

    For numeric type and date- and timestamp types, a ``nmatch()`` is
    performed.

    For boolean type, ``bmatch()`` is performed.

    Any keyword arguments passed to this function are relayed to selected match
    functions, but functions choose what keywords they will handle.
    """
    x = data.get(key, None)
    y = totype(keyword, vtype)
    if vtype in [DATESTAMP, TIMESTAMP, NUMERIC]:
        res =  nmatch(x, y, **kwargs)
    if vtype == BOOLEAN:
        res = bmatch(x, y, **kwargs)
    else:
        res = smatch(x, y, **kwargs)
    return invert ^ res
