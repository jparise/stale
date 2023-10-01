#!/usr/bin/env python

from setuptools import find_packages, setup
from stale import __version__

setup(
    name="stale",
    version=__version__,
    description="Identifies (and optionally removes) stale Pinboard links",
    author="Jon Parise",
    author_email="jon@indelible.org",
    keywords="pinboard",
    url="https://github.com/jparise/stale",
    license="MIT License",
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'],
    packages=find_packages(),
    entry_points={'console_scripts': ['stale = stale:main']},
    zip_safe=True,
)
