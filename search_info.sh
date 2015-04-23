#!/usr/bin/env bash

# Search in metadata
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

Obtain hashes of conent whose metadata match lookup criteria

Uage:
    $SCRIPTNAME KEYWORD

Parameters:
    KEYWORD     search keyword
EOF
}


# naive_search(keyword)
# 
# Perform a naive search by simply grepping files, not taking into account any 
# data structures. Returns a list of matched paths.
#
naive_search() {
    keyword=$1
    grep -i "$keyword" $PATH_WC/info.json | cut -d: -f1
}

# full_search(keyword, key)
#
# Decode JSON and search in specified key
full_search() {
    keyword=$1
    key=$2
    # First perform a naive search to narrow down the search
    naive_search "$keyword" | python "$SRC/filterjson.py" "$keyword" "$key"
}

keyword=$1
key=$2

if [ -z "$keyword" ]
then
    help
    exit 1
fi

if [ -z "$key" ]
then
    paths=$(naive_search "$keyword")
else
    paths=$(full_search "$keyword" "$key")
fi

for path in $paths
do
    echo $(joinseg $(dirname "$path") / $OUTERNET_CONTENT)
done
