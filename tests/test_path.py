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
    'static/css': ('style.css'),
    'static/css/style.css': None,
    'articles': ('article1.html', 'article2.html', 'images'),
    'articles/article1.html': None,
    'articles/article2.html': None,
    'articles/images': ('img1.svg', 'img2.jpg'),
    'articles/images/img1.svg': None,
    'articles/images/img2.jpg': None,
}


# Simplified simulation of os.listdir()
def mock_listdir(path):
    if path.startswith('./'):
        path = path[2:]
    contents = DIRTREE.get(path)
    print(path, contents)
    if contents is None:
        raise OSError()
    return contents


@pytest.yield_fixture
def mock_os():
    """
    Rigged version of os module that uses mock directory structure instead of
    a real one.
    """
    with mock.patch(MOD + '.os') as mos:
        mos.listdir = mock_listdir
        mos.sep = '/'
        mos.path.join = lambda x, y: '/'.join([x, y])
        yield mos


def test_fnwalk(mock_os):
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


def test_fnwalk_shallow(mock_os):
    """
    Given a base path and matcher function, when fnwalk() is called with sallow
    flag, then it returns an iterator that yields only the first path matched.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('.', matcher, shallow=True))) == [
        './articles',
    ]


def test_fnwalk_match_self(mock_os):
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


def test_splitseg():
    """
    Given a string, and segment length, when splitseg() is called, then it
    returns an iterator yielding the segments from the string of specified
    length.
    """
    assert list(mod.splitseg('foobar', 2)) == ['fo', 'ob', 'ar']


def test_splitseg_default_len():
    """
    Given a string and no segment length, when splitseg() is caleld, then it
    yields segments 3 characters long.
    """
    assert list(mod.splitseg('foobar')) == ['foo', 'bar']


def test_segrx():
    """
    Given a string and a length, when segrx() is called, then it returns a
    regular expression fragment that matches a segment of a path of specified
    length where the first part of the segment is given by the string.
    """
    assert mod.segrx('a1', 4) == 'a1[0-9a-f]{2}'


def test_segrx_default_len():
    """
    Given a string and no length, when segrx() is called, then it returns a
    regular expression fragment that matches a segments 3 characters long.
    """
    assert mod.segrx('a1') == 'a1[0-9a-f]{1}'


def test_segrx_zerolen():
    """
    Given a length that is zero or negative number, when segrx() is called,
    then it returns an empty string.
    """
    assert mod.segrx('a1', 0) == ''
    assert mod.segrx('a1', -1) == ''


def test_segrx_no_string():
    """
    Given no string, when segrx() is called, then it returns a regular
    expression framgent that matches any segment of given length.
    """
    assert mod.segrx('') == '[0-9a-f]{3}'


@pytest.mark.parametrize('x', [
    (5, 'accbc/b4965/926[0-9a-f]{2}(?:/[0-9a-f]{5}){3}/[0-9a-f]{2}'),
    (4, 'accb/cb49/6592/6[0-9a-f]{3}(?:/[0-9a-f]{4}){4}'),
    (3, 'acc/bcb/496/592/6[0-9a-f]{2}(?:/[0-9a-f]{3}){5}/[0-9a-f]{2}'),
])
def test_pathrx(x, mock_os):
    """
    Given partial content ID and segment length, when pathrx() is called, then
    it returns a regular expression pattern that matches the full content
    directory path.
    """
    l, rx = x
    cid = 'accbcb4965926'
    assert mod.pathrx(cid, l) == rx


@pytest.mark.parametrize('x', [
    (5, 'accbc/b4965/92678/46e55/90b46/94ee7/69'),
    (4, 'accb/cb49/6592/6784/6e55/90b4/694e/e769'),
    (3, 'acc/bcb/496/592/678/46e/559/0b4/694/ee7/69'),
])
def test_pathrx_full_id(x, mock_os):
    """
    Given full content ID and segment length, when pathrx() is called, then it
    returns a cotent ID that is segmented and concatenated using defalt OS
    separator.
    """
    l, rx = x
    cid = 'accbcb49659267846e5590b4694ee769'
    assert mod.pathrx(cid, l) == rx


def test_pathrx_empty_path(mock_os):
    """
    Given no content ID, when pathrx() is called, then it returns a pattern
    that would match any and all content directories.
    """
    assert mod.pathrx('') == '[0-9a-f]{3}(?:/[0-9a-f]{3}){9}/[0-9a-f]{2}'


@pytest.mark.parametrize('x', [
    (5, 'accbc/b4965/92678/46e55/90b46/94ee7/69'),
    (4, 'accb/cb49/6592/6784/6e55/90b4/694e/e769'),
    (3, 'acc/bcb/496/592/678/46e/559/0b4/694/ee7/69'),
    (5, 'accbc/b4965/92678/46e55/90b46/94ee7/69/info.json'),
    (4, 'accb/cb49/6592/6784/6e55/90b4/694e/e769/info.json'),
    (3, 'acc/bcb/496/592/678/46e/559/0b4/694/ee7/69/info.json'),
    (5, '/home/foo/bar/accbc/b4965/92678/46e55/90b46/94ee7/69/info.json'),
    (4, '/home/foo/bar/accb/cb49/6592/6784/6e55/90b4/694e/e769/info.json'),
    (3, '/home/foo/bar/acc/bcb/496/592/678/46e/559/0b4/694/ee7/69/info.json'),
    (5, '/home/foo/bar/accbc/b4965/92678/46e55/90b46/94ee7/69'),
    (4, '/home/foo/bar/accb/cb49/6592/6784/6e55/90b4/694e/e769'),
    (3, '/home/foo/bar/acc/bcb/496/592/678/46e/559/0b4/694/ee7/69'),
])
def test_cid(x, mock_os):
    """
    Given a path and segment length, when cid() is called, then it returns the
    content ID of the path.
    """
    l, p = x
    cid = 'accbcb49659267846e5590b4694ee769'
    assert mod.cid(p, l) == cid


@pytest.mark.parametrize('x', [
    (5, 'accbc/b4965/92678/46e55/90b46/69'),
    (4, 'accb/cb49/6592/6784/6e55/90b4/694e/'),
    (3, '/bcb/496/592/678/46e/559/0b4/694/ee7/69'),
    (3, '/foo/bar'),
])
def test_cid_partial(x):
    """
    Given partial path, or path that isn't a content directory path, when cid()
    is called, then it returns None.
    """
    l, p = x
    assert mod.cid(p, l) is None
