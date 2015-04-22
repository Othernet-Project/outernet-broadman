#!/usr/bin/env bash

# Find content paths
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

PKG=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
VERSION=$(cat "$PKG/VERSION")

. "$PKG/util/pathutil.sh"

help() {
    cat <<EOF
getpath.sh v$VERSION

Find any paths matching content ID or ID fragment

Usage: 
    getpath.sh ID

Parameters:
    ID      full or partial content ID
EOF
}

cid=$1

if [ -z "$cid" ]
then
    help
    exit 0
fi

find $(pathcards $cid) -maxdepth 0
