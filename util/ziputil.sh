#!/usr/bin/env bash

# Tools for testing zip files
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
#

# chkzip(path)
# ============
#
# Checks zip file at $path. It echos the return code of the zipinfo command.
#
# Example:
# 
#     $ chkzip valid.zip
#     0
#
#     $ chkzip invalid.zip
#     9
#
chkzip() {
    path=$1
    zipinfo "$path" > /dev/null 2>&1
    echo $?
}
