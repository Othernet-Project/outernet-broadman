=================
outernet-broadman
=================

Collection of scripts for managing Outernet content repository.

Installing
==========

Install using pip straight from the repository::

    pip install https://github.com/Outernet-Project/outernet-broadman/archive/master.zip

Git also needs to be installed on your system.

Note that only Unix/Linux systems are supported at this moment.

Environment variables
=====================

Broadman scripts work on a content pool directory. Usually, you need to be in
the root of the content pool when using the commands. To work with the content
pool regardless of the current working directory, you can set the
``OUTERNET_CONTENT`` environment variable to the content pool path.

Overview
========

There are two main aspects when it comes to working with the content pool.
There is a master pool, which contains the actual content, and there are
servers which hold symlinks to content.

Before we begin working on a content pool, we need to initialize it. Use the
following tool for the purpose:

- ``pinit`` - initialize content pool

The following tools are used for working with the content:

- ``zimport`` - import legacy zipball into master pool
- ``update`` - for making changes to content permanent, resetting and reverting
  changes
- ``lschanged`` - listing changed content

Tools for working with metadata metadata:

- ``mcat`` - viewing metadata
- ``med`` - editing metadata
- ``mclean`` - clean up metadta file
- ``filter`` - filter paths according to metadata rules

The following tools are used for navigating the content pool:

- ``getpath`` - obtaining a path to content directory or symlink by content ID
- ``getcid`` - obtaining content ID from content directory path

For managing servers, these tools are available:

- ``srvadd`` - add content to server
- ``srvdel`` - remove content from server
- ``srvsync`` - sync backlog with servers

Using the tools
===============

We won't go into each tool in detail. Instead we'll take a look at some general
principles.

All tools have ``--help`` switch that provides short usage notes and
descriptions of all arguments they take/require.

Most tools can be used as usual by passing arguments to them, or they can be
used in a pipe. When used in a pipe, most tools will take content IDs and/or
paths. You can usually convert between paths and IDs using ``getpath`` and
``getcid`` commands in a pipe.

Most tools will show their status as OK, ERR, or WARN. These are always output
to STDOUT. Additional error information can be output to STDERR. These messages
can be piped to a file to aid troubleshooting.

Apart from conent IDs and paths, tools may have different switches that alter
their behavior. Some tools may require switches to be used.

Tools can and should be used alongside common Unix tools like sed, awk, grep.

The entire content pool is a Git repository. Common git techniques apply.
However, you should avoid using Git directly. 

Broadman tools will usually be able to get you where you need to be without too
much effort.  The tools output commit log messages in a particular
machine-readable format, which is the main reason direct usage of git should be
avoided.

Backlog
=======

Every time a content is added to or removed from a server, this is recorded in
a backlog file located at ``${OUTERNET_CONTENT}/.backlog``. This file is in a
machine-readable format, and automation tools may be added later to help sync
the content pool changes to actual servers.

Reporting bugs
==============

Please report bugs and feature requests to the `issue tracker`_.

.. _issue tracker: https://github.com/Outernet-Project/outernet-broadman/issues
