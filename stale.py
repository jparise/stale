#!/usr/bin/python
#
# stale.py
# Copyright 2010 Jon Parise <jon@indelible.org>

"""Identify (and optionally delete) stale Delicious links"""

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '0.9'

import pydelicious
import sys
import urllib

def main():
    from optparse import OptionParser

    usage = "usage: %prog [options] [query]"
    version = "%prog " + __version__

    parser = OptionParser(usage=usage, version=version, description=__doc__)
    parser.add_option('-u', dest='username', help="Delicious username")
    parser.add_option('-p', dest='password', help="Delicious password")
    parser.add_option('-d', action='store_true', dest='delete',
            help="delete stale links", default=False)
    parser.add_option('-v', action='store_true', dest='verbose',
            help="enable verbose output", default=False)

    (options, args) = parser.parse_args()

    # Perform some basic command line validation.
    if not options.username:
        options.username = raw_input('Username: ')

    if not options.password:
        from getpass import getpass
        options.password = getpass('Password: ')

    if not options.username or not options.password:
        print "A username and password must be provided"
        sys.exit(1)

    # Construct the Delicious API object.
    api = pydelicious.DeliciousAPI(options.username, options.password)

    if options.verbose:
        print "Retrieving all posts for %s" % options.username

    try:
        result = api.posts_all()
    except pydelicious.PyDeliciousUnauthorized:
        print "Authorization failure"
        sys.exit(1)

    if not result or not 'posts' in result:
        print "Failed to retrieve posts"
        sys.exit(1)

    if options.verbose:
        print "Checking %s posts ..." % result['total']

    for post in result['posts']:
        href = post['href']
        stale = False

        try:
            url = urllib.urlopen(href)
        except IOError:
            print "[Err] %s" % href
            stale = True
        else:
            if url.getcode() != 200:
                stale = True
                print "[%3d] %s" % (url.getcode(), href)
            elif options.verbose:
                print "[ OK] %s" % href

        if stale and options.delete: 
            print "  Deleting %s" % href
            try:
                api.posts_delete(href)
            except pydelicious.DeliciousError as e:
                print "  %s" % str(e)

if __name__ == '__main__':
    main()
