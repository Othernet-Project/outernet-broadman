#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

SCRIPTDIR = os.path.dirname(__file__) or '.'
PY3 = sys.version_info >= (3, 0, 0)

from broadman import __version__


def read(fname):
    """ Return content of specified file """
    path = os.path.join(SCRIPTDIR, fname)
    if PY3:
        f = open(path, 'r', encoding='utf8')
    else:
        f = open(path, 'r')
    content = f.read()
    f.close()
    return content


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments for py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='outernet-broadman',
    version=__version__,
    author='Outernet Inc',
    author_email='apps@outernet.is',
    description='Tools for broadcast management',
    license='GPLv3',
    keywords='json, validation, templates, metadata, outernet',
    url='https://github.com/Outernet-Project/bottle-fdsend',
    packages=find_packages(),
    long_description=read('README.rst'),
    install_requires=[
        'outernet-metadata>=0.1.dev1',
    ],
    entry_points={
        'console_scripts': [
            'getpath = broadman.getpath:main',
            'filter = broadman.filterjson:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass={
        'test': PyTest,
    },
)
