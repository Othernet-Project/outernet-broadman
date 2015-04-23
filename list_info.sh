#!/usr/bin/env bash

# List all metadata files
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

Print a list of all metadata files in the content pool

Uage:
    $SCRIPTNAME
EOF
}

ls $PATH_WC/info.json
