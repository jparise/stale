#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

setup(
    name="stale",
    version='1.1',
    description="Identifies (and optionally removes) stale Delicious and Pinboard links",
    author="Jon Parise",
    author_email="jon@indelible.org",
    url="https://github.com/jparise/stale",
    scripts=['stale'],
    install_requires=['pydelicious'],
    license="MIT License",
    classifiers=['Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'],
)
