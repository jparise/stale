# Stale

Stale identifies and deletes stale [Delicious][] and [Pinboard][] links.

You can grab the latest code package by cloning this repository:

    $ git clone https://github.com/jparise/stale.git

... or by downloading the tarball:

    https://github.com/jparise/stale/tarball/master

## Dependencies

Stale is written in [Python][] and depends on the [pydelicious][] package.
You can install pydelicious using `easy_install`::

    $ easy_install pydelicious

... or `pip`:

    $ pip install pydelicious

## Usage

    Usage: stale.py [options]

    Identify (and optionally delete) stale Delicious and Pinboard links

    Options:
    --version    show program's version number and exit
    -h, --help   show this help message and exit
    -u USERNAME  Delicious/Pinboard username
    -p PASSWORD  Delicious/Pinboard password
    -i           use Pinboard instead of Delicious
    -d           delete stale links
    -e           equate errors with staleness
    -v           enable verbose output

[Python]: http://www.python.org/
[Delicious]: http://www.delicious.com/
[Pinboard]: http://pinboard.in/
[pydelicious]: http://code.google.com/p/pydelicious/
