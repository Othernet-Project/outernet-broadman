===============
broadcast-utils
===============

Collection of scripts for managing Outernet content repository.

Prerequisites
=============

The following command line tools are required:

- zip
- unzip
- zipinfo
- md5sum

Python should also be installed.

Naming conventions
==================

All scripts have a .sh extension. Files that contain 'util' in their name are
library modules that should be ``source``d into other scripts rather than used
directly.

Content pool location
=====================

The scripts use a single environment variable ``OUTERNET_CONTENT`` to determine
the location of the content pool. If this variable is not present, scripts
assume that the current working directory is the content pool directory. All
paths scripts work with are calculated from this single path. It is recommended
to set this variable to the correct path to make working with scripts a bit
more flexible.
