=====
Stale
=====

Stale is a simple script that can identify and delete stale `Delicious`_ and
`Pinboard`_ links.

You can grab the latest code package by cloning this repository::

    $ git clone git://github.com/jparise/stale.git

... or by downloading the tarball::

    https://github.com/jparise/stale/tarball/master

Dependencies
------------

Stale is written in `Python`_ and depends on the `pydelicious`_ package.  You
can install pydelicious using ``easy_install``::

    $ easy_install pydelicious

Usage
-----

::

    Usage: stale.py [options]

    Identify (and optionally delete) stale Delicious links

    Options:
    --version    show program's version number and exit
    -h, --help   show this help message and exit
    -u USERNAME  Delicious/Pinboard username
    -p PASSWORD  Delicious/Pinboard password
    -i           use Pinboard instead of Delicious
    -d           delete stale links
    -e           equate errors with staleness
    -v           enable verbose output

.. _Python: http://www.python.org/
.. _Delicious: http://www.delicious.com/
.. _Pinboard: http://pinboard.in/
.. _pydelicious: http://code.google.com/p/pydelicious/
