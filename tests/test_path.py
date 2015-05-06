"""
Tests for broadman.path module

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import broadman.path as mod

MOD = mod.__name__

# Mock directory tree
DIRTREE = {
    '.': ('index.html', 'static', 'articles'),
    'index.html': None,
    'static': ('favicon.ico', 'img', 'css'),
    'static/favicon.ico': None,
    'static/img': ('logo.png', 'header.jpg', 'bg.gif'),
    'static/img/logo.png': None,
    'static/img/header.jpg': None,
    'static/img/bg.gif': None,
    'static/css': ('style.css',),
    'static/css/style.css': None,
    'articles': ('article1.html', 'article2.html', 'images'),
    'articles/article1.html': None,
    'articles/article2.html': None,
    'articles/images': ('img1.svg', 'img2.jpg'),
    'articles/images/img1.svg': None,
    'articles/images/img2.jpg': None,
}


def mock_direntry(name, base_path):
    d = mock.Mock()
    d.path = '/'.join([base_path, name])
    d.name = name
    d.is_file.side_effect = lambda: '.' in name
    return d


# Simplified simulation of os.listdir()
def mock_scan(path):
    base_path = path
    if path.startswith('./'):
        path = path[2:]
    contents = DIRTREE.get(path)
    if contents is None:
        raise OSError()
    contents = [mock_direntry(n, base_path) for n in contents]
    print(path, contents)
    return contents


@pytest.yield_fixture
def mock_scandir():
    """
    Rigged version of scandir module that uses mock directory structure instead
    of a real one.
    """
    with mock.patch(MOD + '.scandir') as msc:
        msc.scandir = mock_scan
        yield msc


@pytest.yield_fixture
def mock_os():
    """
    Rigged version of os module that uses mock directory structure instead of
    a real one.
    """
    with mock.patch(MOD + '.os') as mos:
        mos = mock.Mock()
        mos.sep = '/'
        mos.path.join = lambda x, y: '/'.join([x, y])
        yield mos


def test_fnwalk(mock_scandir):
    """
    Given base path and a matcher function, when fnwalk() is called, it returns
    an iterator that yields paths for which matcher returns True.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('.', matcher))) == [
        './articles',
        './articles/article1.html',
        './articles/article2.html',
        './articles/images',
        './articles/images/img1.svg',
        './articles/images/img2.jpg',
    ]


def test_fnwalk_shallow(mock_scandir):
    """
    Given a base path and matcher function, when fnwalk() is called with sallow
    flag, then it returns an iterator that yields only the first path matched.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('.', matcher, shallow=True))) == [
        './articles',
    ]


def test_fnwalk_match_self(mock_scandir):
    """
    Given a base path and matcher function that matches the base path, when
    fnwalk() is called, it returns an iterator that yields base path, in
    additon to other matched path.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('articles', matcher))) == [
        'articles',
        'articles/article1.html',
        'articles/article2.html',
        'articles/images',
        'articles/images/img1.svg',
        'articles/images/img2.jpg',
    ]


def test_countwalk(mock_scandir):
    """
    Given a base path and matcher function, when countwalk() is called, then it
    returns a count of all files for which the matcher returns True.
    """
    matcher = lambda p: p.endswith('.html')
    assert mod.countwalk('.', matcher) == 3


def test_cidrx():
    """
    Given a string and a length, when cidrx() is called, then it returns a
    regular expression fragment that matches a segment of a path of specified
    length where the first part of the segment is given by the string.
    """
    assert mod.cidrx('a1', 4) == 'a1[0-9a-f]{2}'


def test_cidrx_default_len():
    """
    Given a string and no length, when cidrx() is called, then it returns a
    regular expression fragment that matches a segments 3 characters long.
    """
    assert mod.cidrx('a1') == 'a1[0-9a-f]{30}'


def test_cidrx_zerolen():
    """
    Given a length that is zero or negative number, when cidrx() is called,
    then it returns an empty string.
    """
    assert mod.cidrx('a1', 0) == ''
    assert mod.cidrx('a1', -1) == ''


def test_cidrx_no_string():
    """
    Given no string, when cidrx() is called, then it returns a regular
    expression framgent that matches any segment of given length.
    """
    assert mod.cidrx('') == '[0-9a-f]{32}'


@pytest.mark.parametrize('x', [
    'accbcb49659267846e5590b4694ee769',
    '/home/foo/bar/accbcb49659267846e5590b4694ee769/info.json',
    '/home/foo/bar/accbcb49659267846e5590b4694ee769',
    pytest.mark.xfail('foobar'),
])
def test_cid(x, mock_os):
    """
    Given a path and segment length, when cid() is called, then it returns the
    content ID of the path.
    """
    cid = 'accbcb49659267846e5590b4694ee769'
    assert mod.cid(x) == cid


def test_contentdir(monkeypatch):
    """
    Given content ID and content section name, when contentdir() is called,
    then it returns a full path to the content directory'.
    """
    monkeypatch.setattr(mod, 'POOLDIR', 'foo')
    cid = 'accbcb49659267846e5590b4694ee769'
    server = 'bar'
    expected = 'foo/bar/accbcb49659267846e5590b4694ee769'
    assert mod.contentdir(cid, server) == expected
