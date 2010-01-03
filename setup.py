#!/usr/bin/env python

from distutils.core import setup

version = __import__('stale').__version__

setup(
    name="stale",
    version=version,
    description="Identifies (and optionally removes) stale Delicious links",
    author="Jon Parise",
    author_email="jon@indelible.org",
    url="http://bitbucket.org/jparise/stale/",
    scripts = ['stale.py'],
    license = "MIT License",
    classifiers = ['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
)
