#!/usr/bin/env bash

# Tools for working with MD5-based paths
#
# This is a library module and only contains function definitions. Source into 
# main script(s) to make use of them.


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
