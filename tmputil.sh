#!/usr/bin/env bash

# Tools for working with temporary directories

SYSTEMP=${TMPDIR:-/tmp}

# mktmpdir(pfx)
#
# Creates a temporary directory and echos the path. The temporary diretory is 
# created under the system temporary directory. The directory name is based on 
# current time and optional prefix $pfx.
#
# Default prefix is 'tmp'.
#
# The temporary directory is not automatically cleaned up (except when the 
# operating system performs this task).
#
# Example:
#
#     $ mktmpdir foo
#     /tmp/foo.1429716349
#
#     $ mkdtmpdir
#     /tmp/tmp.1429716349
#
mktmpdir() {
    pfx=${1:-tmp}
    dname="${SYSTEMP}/${pfx}.$(date +%s)"
    mkdir -p "$dname"
    echo $dname
}
