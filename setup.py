import io
import os
import re
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

PKG_NAME = 'deepsmiles'

HERE = os.path.abspath(os.path.dirname(__file__))

PATTERN = r'^{target}\s*=\s*([\'"])(.+)\1$'

AUTHOR = re.compile(PATTERN.format(target='__author__'), re.M)
DOCSTRING = re.compile(r'^([\'"])\1\1(.+)\1\1\1$', re.M)
VERSION = re.compile(PATTERN.format(target='__version__'), re.M)


def parse_init():
    with open(os.path.join(HERE, PKG_NAME, '__init__.py')) as f:
        file_data = f.read()
    return [regex.search(file_data).group(2) for regex in
            (AUTHOR, DOCSTRING, VERSION)]


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.rst')
author, description, version = parse_init()

setup(
    author=author,
    author_email='noel@nextmovesoftware.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    description=description,
    license='License :: OSI Approved :: MIT License',
    long_description=long_description,
    name=PKG_NAME,
    packages=[PKG_NAME],
    platforms='any',
    test_suite = "deepsmiles.testsuite",
    url='http://github.com/nextmovesoftware/deepsmiles',
    version=version,
)
