"""
Functions for working with broadcast database

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sqlite3
import datetime

import sqlize as sql

from . import path


OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError


class DB:
    TABLE = 'broadcasts'
    SCHEMA = """
    create table if not exists broadcasts (
        content_id text,
        server_id text,
        commit_hash text,
        title text,
        url text,
        size integer,
        collected timestamp,
        packed timestamp,
        aired timestamp,
        removed timestamp,
        expires timestamp
    );
    """

    def __init__(self, db=path.BROADCAST):
        self.con = sqlite3.connect(db)
        self.con.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        self.con.executescript(self.SCHEMA)

    def add_content(self, id, server, commit, title, url, size, collected,
                    packed, aired, expires=None):
        q = sql.Insert(self.TABLE, cols=(
            'content_id', 'server_id', 'commit_hash', 'title', 'url', 'size',
            'collected', 'packed', 'aired', 'expires'))
        self.con.execute(str(q), {
            'content_id': id,
            'server_id': server,
            'commit_hash': commit,
            'title': title,
            'url': url,
            'size': size,
            'collected': collected,
            'packed': packed,
            'aired': aired,
            'expires': expires,
        })
        self.con.commit()
        self.con.close()

    def remove_content(self, id):
        q = sql.Update(self.TABLE, 'content_id=:id', removed=':time')
        self.con.execute(str(q), {'id': id, 'time': datetime.datetime.today()})
        self.con.commit()
        self.con.close()
