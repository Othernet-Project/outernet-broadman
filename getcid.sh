#!/usr/bin/env bash

# Get content ID from path
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
#

set -e

SRC=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPTNAME=$(basename ${BASH_SOURCE[0]})
VERSION=$(cat "$SRC/VERSION")

. "$SRC/util/pathutil.sh"

help() {
    cat <<EOF
$SCRIPTNAME v$VERSION

Usage:
    $SCRIPTNAME PATH
    PATH | $SCRIPTNAME

Parameter:
    PATH        path of the content directory
EOF
}

tocid() {
    path=$1
    joined=$(joinseg "$path" / "$OUTERNET_CONTENT")
    echo ${joined:0:32}
}

if [ -t 0 ]
then
    path=$1

    if [ -z "$path" ]
    then
        help
        exit 1
    fi

    tocid "$path"
else
    while read path
    do
        tocid "$path"
    done
fi
