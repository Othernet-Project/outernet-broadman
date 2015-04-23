#!/usr/bin/env bash

# Mark content for broadcast on a satellite
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

set -e

SRC=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPTNAME=$(basename ${BASH_SOURCE[0]})
VERSION=$(cat "$SRC/VERSION")

. "$SRC/util/pathutil.sh"
. "$SRC/util/streamutil.sh"

help() {
    cat <<EOF
$SCRIPTNAME v$VERSION

Mark content with given ID for broadcast in specified stream

Usage:
    $SCRIPTNAME ID STREAM
    ID | $SCRIPTNAME STREAM

Parameters:
    ID          full or partial content ID
    STREAM      stream label
EOF
}

sadd() {
    cid=$1
    label=$2

    if [ -z "$(getstream "$label" || true)" ]
    then
        echo "${label}: no such stream"
        exit 1
    fi

    cpath=$(findpath "$cid")
    cid=$(fullcid $cpath)
    bfile=$(broadcastpath "$cid")

    if [ ! -e "$cpath" ]
    then
        echo "${cpath}: no such directory"
        exit 1
    fi

    if [ -e "$bfile" ]
    then
        grep "^$label" "$bfile" > /dev/null 2>&1
        if [ $? -ne 1 ]
        then
            echo "$cid: already marked for broadcast on $label"
        fi
    fi

    echo "$label" >> "$bfile"
}

if [ -t 0 ]
then
    cid=$1
    label=$2

    if [ -z "$cid" ] || [ -z "$label" ]
    then
        help
        exit 1
    fi

    sadd "$cid" "$laebel"
else
    label=$1

    if [ -z "$label" ]
    then
        help
        exit 1
    fi

    while read cid
    do
        sadd "$cid" "$label"
    done
fi
