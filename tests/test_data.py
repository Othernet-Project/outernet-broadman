"""
Tests for broadman.data module

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime

import pytest

import broadman.data as mod

MOD = mod.__name__

parametrize = pytest.mark.parametrize
xfail = pytest.mark.xfail


DATA = {
    'foo': 'Quick brown Fox jumps over Lazy old Dog',
    'bar': 12,
    'baz': datetime.datetime(2015, 3, 15, 12, 15),
    'fee': None,
    'fam': False,
}


def test_parse_date():
    """
    Given a string datestamp in YYYY-MM-DD format, when parse_date() is called,
    then it returns a datetime object matching the given date.
    """
    assert mod.parse_date('2015-04-25') == datetime.datetime(2015, 4, 25)


def test_parse_date_invalid():
    """
    Given a string that is not in correct format, when parse_date() is called,
    then it raises ValueError.
    """
    with pytest.raises(ValueError):
        mod.parse_date('foo')


def test_parse_ts():
    """
    Given a timestamp string in YYYY-MM-DD HH:MM:SS format, when parse_ts() is
    called, then it returns a datetime instance for the given timestamp.
    """
    assert mod.parse_ts('2015-04-25 12:23:11') == datetime.datetime(
        2015, 4, 25, 12, 23, 11)


def test_parse_ts_invalid():
    """
    Given a string that is not in correct format, when parse_ts() is called,
    then it raises ValueError.
    """
    with pytest.raises(ValueError):
        mod.parse_ts('foo')


def test_parse_num():
    """
    Given a string representation of a number, when parse_num() is called, then
    it returns a float for that number.
    """
    assert mod.parse_num('1') == 1.0
    assert mod.parse_num('2.3') == 2.3
    assert mod.parse_num('-1') == -1.0


@parametrize('x', [
    'no', 'false', 'null', '0', 'No', 'False', 'NULL', '0', xfail('true'),
    xfail('yes')])
def test_parse_bool(x):
    """
    Given a string that is one of no, false, null or 0, when pase_bool() is
    called, then it returns False.
    """
    assert mod.parse_bool(x) is False


@parametrize('x', [
    ('d', '2015-04-25', datetime.datetime(2015, 4, 25)),
    ('t', '2015-04-25 15:00:21', datetime.datetime(2015, 4, 25, 15, 0, 21)),
    ('n', '1.2', 1.2),
    ('n', '1', 1.0),
    ('n', '-2', -2.0),
    ('n', '0.0', 0.0),
    ('b', 'no', False),
    ('b', 'NULL', False),
    ('b', '0', False),
    ('b', 'yes', True),
    (None, 'foo', 'foo'),
    xfail(('d', '2015-Apr-25', datetime.datetime(2015, 4, 25))),
    xfail(('t', '15-4-25 3:00pm', datetime.datetime(2015, 4, 25, 15, 0, 21))),
    xfail(('n', 'foo', 1.0)),
    xfail(('unknown', 'foo', 'foo')),
])
def test_totype(x):
    """
    Given a type marker and a string, when totype() is called, then it returns
    a value coerced to a Python type according to conversion rules.
    """
    marker, s, val = x
    assert mod.totype(s, marker) == val


def test_smatch():
    """
    Given a two values, x and y, when smatch() is called, then it performs a
    case-insensitive is in match of y against x.
    """
    assert mod.smatch('Foo Bar Baz', 'bar')
    assert not mod.smatch('Foo Bar Baz', 'fam')


def test_smatch_xmatch():
    """
    Given two values, x and y, when smatch() is called with xmatch flag set
    to True, then it performs a full-length match of y against x.
    """
    assert mod.smatch('Foo Bar Baz', 'foo bar baz', xmatch=True)
    assert not mod.smatch('Foo Bar Baz', 'bar', xmatch=True)


def test_smatch_icase():
    """
    Given two values, x and y, when smatch() is called with icase flag set to
    False, then it performs all matches case-sensitively.
    """
    assert mod.smatch('Foo Bar Baz', 'Bar', icase=False)
    assert not mod.smatch('Foo Bar Baz', 'bar', icase=False)
    assert mod.smatch('Foo Bar Baz', 'Foo Bar Baz', xmatch=True, icase=False)
    assert not mod.smatch('Foo Bar Baz', 'foo bar baz', xmatch=True,
                          icase=False)


def test_nmatch():
    """
    Given two values, x and y, when nmatch() is called, then it tests the
    values for equality.
    """
    assert mod.nmatch(1, 1)
    assert not mod.nmatch(1, 0)


def test_nmatch_lt():
    """
    Given two values, x and y, when nmatch() is called with lt flag set to
    True, then it performs a less than test.
    """
    assert mod.nmatch(1, 3, lt=True)
    assert not mod.nmatch(1, -2, lt=True)


def test_nmatch_gt():
    """
    Given two values, x and y, when nmatch() is called with gt flag set to
    True, then it performs a greater than test.
    """
    assert mod.nmatch(1, -2, gt=True)
    assert not mod.nmatch(1, 3, gt=True)


def test_bmatch():
    """
    Given two values, x and y, when bmatch() is called, then an equivalence
    test is performed.
    """
    assert mod.bmatch(True, True)
    assert mod.bmatch(1, 1)
    assert not mod.bmatch(True, False)
