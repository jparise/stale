#!/usr/bin/env python
#
# Copyright (c) 2010-2023 Jon Parise <jon@indelible.org>
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

import enum
import getpass
import json
import os
import re
import sys

from http.client import HTTPResponse
from typing import Optional
from urllib.error import HTTPError
from urllib.parse import urldefrag, urlencode, urlparse, urljoin
from urllib.request import HTTPHandler, HTTPSHandler, OpenerDirector, Request, build_opener, urlopen

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '2.0-dev'

PINBOARD_API_BASE = 'https://api.pinboard.in/v1/'
USER_AGENT = (
    f"Mozilla/5.0 (compatible; stale/{__version__}; +https://github.com/jparise/stale)"
)


class Color(enum.StrEnum):
    normal = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    purple = '\033[35m'
    cyan = '\033[36m'


def pinboard_call(path, token, **kwargs):
    """Make a Pinboard API request and return a JSON-parsed response."""
    params = kwargs.copy()
    params['auth_token'] = token
    params['format'] = 'json'

    url = urljoin(PINBOARD_API_BASE, path)
    url += '?' + urlencode(params)

    request = Request(url, headers={'User-Agent': USER_AGENT})
    response = urlopen(request)

    return json.load(response)


def check_url(opener: OpenerDirector, url: str, timeout: Optional[float] = None) -> HTTPResponse:
    """Check the given URL by issuring a HEAD request."""
    # We don't want to include a fragment in our request.
    url, _fragment = urldefrag(url)

    # Attempt to open the target URL using a HEAD request.
    request = Request(url, headers={'User-Agent': USER_AGENT}, method='HEAD')

    return opener.open(request, timeout=timeout)


def supports_color():
    # Windows only supports colors if ANSICON is defined.
    if sys.platform == 'win32' and 'ANSICON' not in os.environ:
        return False

    # Otherwise, we assume all TTYs support ANSI color.
    return getattr(sys.stdout, 'isatty', False)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('-t', '--token',
                        help="your Pinboard API token ('username:hex-values')")
    parser.add_argument('--ignore', nargs='+', type=re.compile,
                        help="ignore links from these hosts", metavar='REGEX')
    parser.add_argument('-d', '--delete', action='store_true',
                        help="delete stale links")
    parser.add_argument('-e', action='store_true', dest='errors',
                        help="equate errors with staleness")
    parser.add_argument('--timeout', type=float, default=5,
                        help="HTTP connection timeout (in seconds)")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="enable verbose output")
    parser.add_argument('--debug', action='store_true',
                        help="enable debugging output")
    parser.add_argument('--version', action='version', version=__version__)

    args = parser.parse_args()

    if not args.token:
        try:
            args.token = getpass.getpass('API Token: ')
        except KeyboardInterrupt:
            return 0

    try:
        posts = pinboard_call('posts/all', args.token)
    except Exception as e:
        print("Failed to retrieve posts:", e)
        return 1

    if not posts:
        print("No posts were retrieved.")
        return 1

    if args.verbose:
        print(f"Checking {len(posts)} posts ...")

    if supports_color():
        def report(color: Color, code:str, url: str):
            print(f"{color}[{code}] {Color.normal}{url}")
    else:
        def report(color: Color, code:str, url: str):
            print(f"[{code}] {url}")

    opener = build_opener(
        HTTPHandler(debuglevel=int(args.debug)),
        HTTPSHandler(debuglevel=int(args.debug)),
    )

    # The set of HTTP status codes that we consider indicators of "staleness"
    # includes all client errors (4xx) except for:
    #
    #  403: we lack support for sending credentials with our requests for
    #       sites that require authorization
    stale_codes = frozenset(range(400, 499)) - {403}

    for post in posts:
        url = post['href']
        stale = False

        # If we have some hostnames to ignore, parse the URL and check if it
        # matches one of the patterns.
        if args.ignore:
            parsed = urlparse(url)
            for pattern in args.ignore:
                if pattern.match(parsed.hostname):
                    report(Color.cyan, 'Skip', url)
                    continue

        try:
            result = check_url(opener, url, timeout=args.timeout)
        except KeyboardInterrupt:
            break
        except HTTPError as e:
            stale = e.code in stale_codes
            report(Color.red if stale else Color.purple, str(e.code), url)
        except OSError as e:
            # Timeouts are considered transient (non-fatal) errors.
            if isinstance(getattr(e, 'reason', e), TimeoutError):
                report(Color.yellow, "Timeout", url)
                continue

            # All other errors are considered request failures.
            report(Color.red, "!!", url)
            print('> ' + str(e).replace('\n', '\n> '))
            if args.errors:
                stale = True
        else:
            code = result.getcode()
            if code in stale_codes:
                stale = True
                report(Color.red, str(code), url)
            elif args.verbose:
                report(Color.green, "OK", url)

        if stale and args.delete:
            print(f"  Deleting {url}")
            try:
                pinboard_call('posts/delete', args.token, url=url)
            except Exception as e:
                print('> ' + str(e))


if __name__ == '__main__':
    sys.exit(main())
