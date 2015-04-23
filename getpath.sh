#!/usr/bin/env bash

# Find content paths
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

SRC=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPTNAME=$(basename ${BASH_SOURCE[0]})
VERSION=$(cat "$SRC/VERSION")

. "$SRC/util/pathutil.sh"

help() {
    cat <<EOF
$SCRIPTNAME v$VERSION

Find any paths matching content ID or ID fragment

Usage: 
    $SCRIPTNAME ID
    ID | $SCRIPTNAME

Parameters:
    ID      full or partial content ID
EOF
}

if [ -t 0 ]
then
    cid=$1

    if [ -z "$cid" ]
    then
        help
        exit 0
    fi

    findpath "$cid"
else
    while read cid
    do
        findpath "$cid"
    done
fi
