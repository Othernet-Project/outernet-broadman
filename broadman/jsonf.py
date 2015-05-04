"""
Functions for storing and loading JSON data

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json


try:
    FILE_ERRORS = (IOError, OSError, FileNotFoundError)
except NameError:
    FILE_ERRORS = (IOError, OSError)


class LoadError(Exception):
    pass


def save(path, data):
    """ Save data to a file at given path """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def load(path):
    """ Load data from a file at given path """
    try:
        with open(path, 'r') as f:
            try:
                return json.load(f, encoding='utf8')
            except ValueError:
                raise LoadError('malformed json')
    except FILE_ERRORS:
        raise LoadError('file not found or not readable')
