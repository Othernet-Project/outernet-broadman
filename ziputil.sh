#!/usr/bin/env bash

# Tools for testing zip files


# chkzip(path)
#
# Checks zip file at $path. It echos the return code of the zipinfo command.
#
# Example:
# 
#     $ chkzip valid.zip
#     0
#
#     $ chkzip invalid.zip
#     9
#
chkzip() {
    path=$1
    zipinfo "$path" > /dev/null 2>&1
    echo $?
}
