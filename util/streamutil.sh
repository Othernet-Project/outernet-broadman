#!/usr/bin/env bash

# Tools for working with data stream information
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

STREAMUTIL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

. "$STREAMUTIL_DIR/pathutil.sh"

STREAMDEF=$OUTERNET_CONTENT/.streamdef

# getstream(label)
# ================
#
# Get data for a single stream matching label
#
getstream() {
    label=$1
    grep "^$label " "$STREAMDEF"
}

# getlabels()
# ===========
#
# Get all labels defined in the streamdef file
#
getlables() {
    cat "$STEAMDEF" | cut -d' ' -f1
}

# host(def)
# =========
#
# Get the host of a single stream definition
host() {
    def=$1
    echo -n "$def" | cut -d' ' -f2
}

# user(def)
# =========
#
# Get the username of a single stream definition
user() {
    def=$1
    echo -n "$def" | cut -d' ' -f3
}

# pass(def)
# =========
#
# Get the password of a single stream definition
pass() {
    def=$1
    echo -n "$def" | cut -d' ' -f4
}
