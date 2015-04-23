#!/usr/bin/env bash

# Tools for working with MD5-based paths
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.


OUTERNET_CONTENT=${OUTERNET_CONTENT:-$(pwd)}
PATH_WC="$OUTERNET_CONTENT/*/*/*/*/*/*/*/*/*/*/*"

# md5(s)
#
# Convert string $s to MD5 hexdigest.
#
# For example:
#
#     $ md5 foo
#     acbd18db4cc2f85cedef654fccc4a4d8
# 
md5() {
    s=$1
    echo -n "$s" | md5sum | cut -d' ' -f1  
}

# splitseg(s, d)
#
# Splits string $s into segments of 3 digits + remainder and concatenates them 
# using delimiter $d.
#
# Default delimiter is '/'.
#
# For example:
#
#    $ splitseg 123456789
#    123/456/789
#
#    $ splitseg 1234567890
#    123/456/789/0
#
#    $ splitseg 1234567890 '#'
#    123#456#789#0
# 
splitseg() {
    s=$1
    delim=${2:-/}
    echo -n "$s" | sed -r "s|(.{3})|\1$delim|g"
}

# joinseg(s, d, pfx)
#
# Given a string $s with segments delimited by $d, and a prefix $pfx, returns 
# the string without the prefix and the delimiters.
# 
# For example:
#
#    $ joinseg /foo/123/456/789/0 /
#    foo1234567890
#
#    $ joinseg /foo/123/456/789/0 / /foo
#    1234567890
#
joinseg() {
    s=$1
    d=${2:-/}
    pfx=$3
    echo -n "$1" | sed -r "s|^$pfx||" | sed -r "s|$d||g"
}

# pathcards(s, len)
#
# Given a string $s, contruct a path that converts missing segments into
# wildcards. The $len argument defaults to 32 (length of MD5 hexdigest) and it
# determines the number of widcards needed. String may be longer than $len, but 
# that is not checked by this function.
#
# Example:
#
#     $ pathcards ffbb8cd28
#     ffb/b8c/d28/*/*/*/*/*/*/*/*
#
pathcards() {
    s=$1
    len=${2:-32}
    slen=${#s}
    diff=$(expr $len - $slen)
    if [ $diff > 0 ]
    then
        filler=$(printf 'X%.0s' $(seq 1 $diff))
        s=${s}$filler
    fi
    echo -n $(splitseg "$s") | sed -r 's|X+|\*|g'
}

# findpath(cid)
#
# Get paths matching partial ID $cid
#
findpath() {
    cid=$1
    find $(pathcards "$cid") -maxdepth 0
}

# fullcid(path)
#
# Get full content ID from given path
#
fullcid() {
    path=$1
    echo $(joinseg "$path" / $OUTERNET_CONTENT)
}

# contentpath(cid)
#
# Get full path for content with specified ID
#
contentpath() {
    cid=$1
    echo "$OUTERNET_CONTENT/$(splitseg "$cid")"
}

# broadcastpath(cid)
#
# Get path to broadcast file for given content ID
#
broadcastpath() {
    cid=$1
    echo "$(contentpath "$cid")/.broadcast"
}

# infopath(cid)
#
# Get path to metadta file for given content ID
#
infopath() {
    cid=$1
    echo "$(contentpath "$cid")/info.json"
}
