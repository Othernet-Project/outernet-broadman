#!/usr/bin/env bash

# My awesome script
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
#

SRC=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPTNAME=$(basename ${BASH_SOURCE[0]})
VERSION=$(cat "$SRC/VERSION")
PROG=${EDITOR:-vi}

. "$SRC/util/tmputil.sh"

help() {
    cat <<EOF
$SCRIPTNAME v$VERSION

Usage:
    $SCRIPTNAME PATH
    PATH | $SCRIPTNAME

Parameter:
    PATH    path to metadata file

Set the value of EDITOR environment variable to desired program.
EOF
}

main() {
    path=$1

    tpath=$(mktmppath editmeta json)
    cat "$path" > "$tpath"

    while true
    do
        $PROG "$tpath"
        metacheck "$tpath"
        if [ $? -eq 0 ]
        then
            echo -n "Saving metadata..."
            cat "$tpath" > "$path"
            rm "$tpath"
            echo DONE
            exit 0
        fi
        echo "1) Continue editing"
        echo "2) Revert and start over"
        echo "3) Abort"
        read -n1 -p "What do you want to do? [1] " choice
        echo
        case $choice in
            2)
                cat "$path" > "$tpath"
                ;;
            3)
                rm "$tpath"
                exit 0
                ;;
        esac
    done
}

if [ -t 0 ]
then
    path=$1

    if [ -z "$path" ]
    then
        help
        exit 1
    fi

    main "$path"
else
    while read path
    do
        main "$path"
    done
fi
