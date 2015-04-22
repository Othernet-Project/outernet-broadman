#!/usr/bin/env bash

# Tools for working with log files

PKG=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

. "$PKG/tmputil.sh"

LOGFILE=$SYSTEMP/log_$(date +%Y%m%d%H%M%S).log

# mklog(pfx)
#
# Create a log file with prefix $pfx in the system temporary directory. Default 
# prefix is 'log'. Filenames always contain the timestamp in '%Y%m%d%H%M%S' 
# format.
#
mklog() {
    pfx=${1:-log}
    LOGFILE=$SYSTEMP/${pfx}_$(date +%Y%m%d%H%M%S).log
    echo '' > "$LOGFILE"
}

# log(msg)
#
# Log a message to the logfile
#
log() {
    msg=$*
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" >> "$LOGFILE"
}


# plog()
#
# Rread from pipe and log
#
plog() {
    while read msg
    do
        log $msg
    done
}


