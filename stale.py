#!/usr/bin/env python
#
# Copyright (c) 2010-2016 Jon Parise <jon@indelible.org>
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

"""Identify (and optionally delete) stale Pinboard links."""

import json
import sys
import urllib
import urllib2
import urlparse

try:
    import curses
except:
    curses = None

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '2.0-dev'

PINBOARD_API_BASE = 'https://api.pinboard.in/v1/'
USER_AGENT = \
    'Mozilla/5.0 (compatible; stale/{}; +https://github.com/jparise/stale)' \
    .format(__version__)

colors = {'normal': '', 'green': '', 'red': ''}


def pinboard_call(path, token, **kwargs):
    """Make a Pinboard API request and return a JSON-parsed response."""
    params = kwargs.copy()
    params['auth_token'] = token
    params['format'] = 'json'

    url = urlparse.urljoin(PINBOARD_API_BASE, path)
    url += '?' + urllib.urlencode(params)

    request = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(url)

    return json.load(response)


def check_url(url):
    """Check the given URL by issuring a HEAD request."""
    # We don't want to include a fragment in our request.
    url, fragment = urlparse.urldefrag(url)

    # Attempt to open the target URL using a HEAD request.
    request = urllib2.Request(url)
    request.get_method = lambda: 'HEAD'
    request.add_header('User-Agent', USER_AGENT)

    return urllib2.urlopen(request)


def setup_colors():
    has_colors = False
    if curses and sys.stdout.isatty():
        try:
            curses.setupterm()
            has_colors = curses.tigetnum('colors') > 0
        except:
            pass

    if has_colors:
        global colors
        fg = curses.tigetstr('setaf') or curses.tigetstr('setf') or ''
        colors['normal'] = curses.tigetstr('sgr0')
        colors['green'] = curses.tparm(fg, 2)
        colors['red'] = curses.tparm(fg, 1)


def report(code, href):
    if str(code) == 'OK':
        color = 'green'
    else:
        color = 'red'
    print "%s[%3s] %s%s" % (colors[color], code, colors['normal'], href)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--token', help='your Pinboard API token')
    parser.add_argument('-d', '--delete', action='store_true',
                        help="delete stale links", default=False)
    parser.add_argument('-e', action='store_true', dest='errors',
                        help="equate errors with staleness", default=False)
    parser.add_argument('-v', action='store_true', dest='verbose',
                        help="enable verbose output", default=False)
    parser.add_argument('--version', action='version', version=__version__)

    args = parser.parse_args()

    if not args.token:
        from getpass import getpass
        args.token = getpass('API Token: ')

    setup_colors()

    try:
        posts = pinboard_call('posts/all', token=args.token)
    except Exception as e:
        print "Failed to retrieve posts:", e
        sys.exit(1)

    if not posts:
        print "No posts were retrieved."
        sys.exit(1)

    if args.verbose:
        print "Checking %s posts ..." % len(posts)

    for post in posts:
        href = post['href']
        stale = False

        try:
            result = check_url(href)
        except KeyboardInterrupt:
            break
        except IOError as e:
            report('Err', href)
            print "  %s" % e
            if args.errors:
                stale = True
        else:
            code = result.getcode()
            if code / 100 == 4 and code != 403:
                stale = True
                report(str(code), href)
            elif args.verbose:
                report('OK', href)

        if stale and args.delete:
            print "  Deleting %s" % href
            try:
                pinboard_call('posts/delete', token=args.token, url=href)
            except Exception as e:
                print "  %s" % str(e)

if __name__ == '__main__':
    main()
