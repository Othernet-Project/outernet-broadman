"""
Functions for invoking editors

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import subprocess


DEFAULT_EDITOR = 'vi'
EDITOR = os.environ.get('EDITOR', DEFAULT_EDITOR)


def edit(p):
    subprocess.call([EDITOR, p])
