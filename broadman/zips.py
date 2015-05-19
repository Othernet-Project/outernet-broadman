"""
Functions for working with zipfiles

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import zipfile

from . import path


def zcid(p):
    """ Extracts the content ID from zip file name """
    return os.path.splitext(os.path.basename(p))[0]


def check(p):
    z = zipfile.ZipFile(p)
    for n in z.namelist():
        if n.startswith('/'):
            z.close()
            raise ValueError('content using absolute path ({})'.format(n))
    z.close()


def unzip(p, dest):
    """ Extracts all zip file sto destination folders and closes the file """
    z = zipfile.ZipFile(p)
    z.extractall(dest)
    z.close()


def pack(zpath, src):
    """ Create a new zip file from the specified directory """
    hash = os.path.splitext(os.path.basename(zpath))[0]
    zfile = zipfile.ZipFile(zpath, mode='w', compression=zipfile.ZIP_DEFLATED)
    for f in path.fnwalk(src, lambda x: os.path.isfile(x)):
        zipname = os.path.join(hash, os.path.relpath(f, src))
        zfile.write(f, arcname=zipname)
    zfile.close()
    return zpath
