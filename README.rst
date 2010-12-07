=====
Stale
=====

Stale is a simple script that can identify and delete stale `Delicious`_ links.

You can grab the latest code package by cloning this repository::

    $ git clone git://github.com/jparise/stale.git

Dependencies
------------

Stale is written in `Python`_ and depends on the `pydelicious`_ package.

Usage
-----

::

    Usage: stale.py [options]

    Identify (and optionally delete) stale Delicious links

    Options:
    --version    show program's version number and exit
    -h, --help   show this help message and exit
    -u USERNAME  Delicious username
    -p PASSWORD  Delicious password
    -d           delete stale links
    -e           equate errors with staleness
    -v           enable verbose output

.. _Python: http://www.python.org/
.. _Delicious: http://www.delicious.com/
.. _pydelicious: http://code.google.com/p/pydelicious/
