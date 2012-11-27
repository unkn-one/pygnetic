#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup
import pygnetic

setup(
    name='pygnetic',
    version=pygnetic.__version__,
    description='Network library for Pygame',
    author='Szymon Wróblewski',
    author_email='bluex0@gmail.com',
    url='https://bitbucket.org/bluex/pygame_network',
    keywords='pygame network networking',
    packages=['pygnetic', 'pygnetic.network', 'pygnetic.serialization'],
    license=open('LICENSE.txt').readline().strip(),
    long_description=open('README.txt').read(),
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: pygame',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
)
