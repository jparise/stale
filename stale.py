#!/usr/bin/python
#
# Copyright (c) 2010 Jon Parise <jon@indelible.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Identify (and optionally delete) stale Delicious and Pinboard links"""

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '1.1'

import pydelicious
import sys
import urllib

PINBOARD_API_HOST = 'api.pinboard.in'
PINBOARD_API_PATH = 'v1'
PINBOARD_API_REALM = 'API'
PINBOARD_API = "https://%s/%s" % (PINBOARD_API_HOST, PINBOARD_API_PATH)

def pinboard_api_opener(user, passwd):
    import urllib2

    manager = urllib2.HTTPPasswordMgr()
    manager.add_password(PINBOARD_API_REALM, PINBOARD_API_HOST, user, passwd)
    auth_handler = urllib2.HTTPBasicAuthHandler(manager)

    handlers = (auth_handler, pydelicious.DeliciousHTTPErrorHandler())

    if pydelicious.DEBUG:
        httpdebug = urllib2.HTTPHandler(debuglevel=DEBUG)
        handlers += (httpdebug,)

    if pydelicious.HTTP_PROXY or pydelicious.HTTPS_PROXY:
        proto = {}
        if pydelicious.HTTPS_PROXY:
            proto['https'] = pydelicious.HTTPS_PROXY
        if pydelicious.HTTP_PROXY:
            proto['http'] = pydelicious.HTTP_PROXY
        handlers += (urllib2.ProxyHandler( proto ),)

    return urllib2.build_opener(*handlers)

def pinboard_api_request(path, params=None, user='', passwd='', throttle=True,
        opener=None):
    if throttle:
        pydelicious.Waiter()

    if params:
        url = "%s/%s?%s" % (PINBOARD_API, path, urllib.urlencode(params))
    else:
        url = "%s/%s" % (PINBOARD_API, path)

    if pydelicious.DEBUG: print >>sys.stderr, \
            "pinboard_api_request: %s" % url

    if not opener:
        opener = pinboard_api_opener(user, passwd)

    fl = pydelicious.http_request(url, opener=opener)

    if pydelicious.DEBUG>2: print >>sys.stderr, \
            pydelicious.pformat(fl.info().headers)

    return fl

def sanitize_url(url):
    hash_position = url.find('#')
    if hash_position != -1:
        return url[0:hash_position]
    return url

def main():
    from optparse import OptionParser

    parser = OptionParser(version="%prog " + __version__, description=__doc__)
    parser.add_option('-u', dest='username', help="Delicious/Pinboard username")
    parser.add_option('-p', dest='password', help="Delicious/Pinboard password")
    parser.add_option('-i', action='store_true', dest='pinboard',
            help="use Pinboard instead of Delicious", default=False)
    parser.add_option('-d', action='store_true', dest='delete',
            help="delete stale links", default=False)
    parser.add_option('-e', action='store_true', dest='errors',
            help="equate errors with staleness", default=False)
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

    # Select the appropriate API handler functions for the chosen service.
    api_request = pydelicious.dlcs_api_request
    api_opener = pydelicious.dlcs_api_opener
    if options.pinboard:
        api_request = pinboard_api_request
        api_opener = pinboard_api_opener

    # Construct the Delicious API object.
    api = pydelicious.DeliciousAPI(options.username, options.password,
            api_request=api_request, build_opener=api_opener)

    if options.verbose:
        service = 'Pinboard' if options.pinboard else 'Delicious'
        print "Retrieving all %s posts for %s" % (service, options.username)

    try:
        result = api.posts_all()
    except pydelicious.PyDeliciousUnauthorized:
        print "Authorization failure"
        sys.exit(1)

    if not result or not 'posts' in result:
        print "Failed to retrieve posts"
        sys.exit(1)

    if options.verbose:
        print "Checking %s posts ..." % len(result['posts'])

    for post in result['posts']:
        href = post['href']
        stale = False

        try:
            url = urllib.urlopen(sanitize_url(href))
        except IOError as e:
            print "[Err] %s" % href
            print "  %s" % e
            if options.errors:
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
