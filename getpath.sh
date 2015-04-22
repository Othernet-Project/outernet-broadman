#!/usr/bin/env bash

# Find content paths

PKG=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

. "$PKG/pathutil.sh"

VERSION=$(cat "$PKG/VERSION")

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
