#!/usr/bin/env python
#
# Copyright (c) 2010-2019 Jon Parise <jon@indelible.org>
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

from __future__ import print_function

import collections
import getpass
import json
import os
import re
import ssl
import sys

try:
    from urllib.parse import urldefrag, urlencode, urlparse, urljoin
    from urllib.request import Request, urlopen
except ImportError:
    from urlparse import urldefrag, urljoin, urlparse
    from urllib import urlencode
    from urllib2 import Request, urlopen

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '2.0-dev'

PINBOARD_API_BASE = 'https://api.pinboard.in/v1/'
USER_AGENT = \
    'Mozilla/5.0 (compatible; stale/{}; +https://github.com/jparise/stale)' \
    .format(__version__)

COLORS = collections.defaultdict(str)


def pinboard_call(path, token, **kwargs):
    """Make a Pinboard API request and return a JSON-parsed response."""
    params = kwargs.copy()
    params['auth_token'] = token
    params['format'] = 'json'

    url = urljoin(PINBOARD_API_BASE, path)
    url += '?' + urlencode(params)

    request = Request(url)
    request.add_header('User-Agent', USER_AGENT)
    response = urlopen(url)

    return json.load(response)


def check_url(url):
    """Check the given URL by issuring a HEAD request."""
    # We don't want to include a fragment in our request.
    url, fragment = urldefrag(url)

    # Attempt to open the target URL using a HEAD request.
    request = Request(url)
    request.get_method = lambda: 'HEAD'
    request.add_header('User-Agent', USER_AGENT)

    return urlopen(request)


def report(code, url):
    if str(code) == 'OK':
        color = 'green'
    else:
        color = 'red'
    print('{}[{}] {}{}'.format(COLORS[color], code, COLORS['normal'], url))


def supports_color():
    # Windows only supports colors if ANSICON is defined.
    if sys.platform == 'win32' and 'ANSICON' not in os.environ:
        return False

    # Otherwise, we assume all TTYs support ANSI color.
    return getattr(sys.stdout, 'isatty', False)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--token',
                        help="your Pinboard API token ('username:hex-values')")
    parser.add_argument('--ignore', nargs='+', type=re.compile,
                        help="ignore links from these hosts", metavar='REGEX')
    parser.add_argument('-d', '--delete', action='store_true',
                        help="delete stale links", default=False)
    parser.add_argument('-e', action='store_true', dest='errors',
                        help="equate errors with staleness", default=False)
    parser.add_argument('-v', action='store_true', dest='verbose',
                        help="enable verbose output", default=False)
    parser.add_argument('--version', action='version', version=__version__)

    args = parser.parse_args()

    if not args.token:
        try:
            args.token = getpass.getpass('API Token: ')
        except KeyboardInterrupt:
            sys.exit(0)

    # If the terminal supports ANSI color, set up our color codes.
    if supports_color():
        COLORS['normal'] = '\033[0m'
        COLORS['green'] = '\033[32m'
        COLORS['red'] = '\033[31m'

    try:
        posts = pinboard_call('posts/all', token=args.token)
    except Exception as e:
        print("Failed to retrieve posts:", e)
        sys.exit(1)

    if not posts:
        print("No posts were retrieved.")
        sys.exit(1)

    if args.verbose:
        print("Checking {} posts ...".format(len(posts)))

    for post in posts:
        url = post['href']
        stale = False

        # If we have some hostnames to ignore, parse the URL and check if it
        # matches one of the patterns.
        if args.ignore:
            parsed = urlparse(url)
            for pattern in args.ignore:
                if pattern.match(parsed.hostname):
                    report('Skip', url)
                    continue

        try:
            result = check_url(url)
        except KeyboardInterrupt:
            break
        except (IOError, ssl.CertificateError) as e:
            report('!!', url)
            print('> ' + str(e).replace('\n', '\n> '))
            if args.errors:
                stale = True
        else:
            code = result.getcode()
            if code / 100 == 4 and code != 403:
                stale = True
                report(str(code), url)
            elif args.verbose:
                report('OK', url)

        if stale and args.delete:
            print("  Deleting {}".format(url))
            try:
                pinboard_call('posts/delete', token=args.token, url=url)
            except Exception as e:
                print('> ' + str(e))


if __name__ == '__main__':
    main()
