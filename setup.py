#!/usr/bin/env python

from distutils.core import setup

setup(
    name="stale",
    version='1.1',
    description="Identifies (and optionally removes) stale Delicious and Pinboard links",
    author="Jon Parise",
    author_email="jon@indelible.org",
    url="https://github.com/jparise/stale",
    scripts = ['stale'],
    license = "MIT License",
    classifiers = ['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
)
