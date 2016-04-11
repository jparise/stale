=====
Stale
=====

Stale identifies and deletes stale `Pinboard`_ links.

You can grab the latest code package by cloning this repository::

    $ git clone https://github.com/jparise/stale.git

... or by downloading the tarball::

    https://github.com/jparise/stale/tarball/master


Usage
-----

::

    usage: stale.py [-h] [-t TOKEN] [-d] [-e] [-v] [--version]

    Identify (and optionally delete) stale Pinboard links.

    optional arguments:
    -h, --help            show this help message and exit
    -t TOKEN, --token TOKEN
                            your Pinboard API token
    -d, --delete          delete stale links
    -e                    equate errors with staleness
    -v                    enable verbose output
    --version             show program's version number and exit

You can find your personal Pinboard API token in your `Settings`_.

.. _Pinboard: http://pinboard.in/
.. _Settings: https://pinboard.in/settings/password
