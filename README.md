# Stale

Stale identifies and deletes stale [Pinboard](http://pinboard.in/) links.

You can grab the latest code package by cloning this repository:

    $ git clone https://github.com/jparise/stale.git

... or by downloading the [latest tarball][].


## Usage

```
usage: stale.py [-h] [-t TOKEN] [--ignore REGEX [REGEX ...]] [-d] [-e] [--timeout TIMEOUT] [-v] [--version]

Identify (and optionally delete) stale Pinboard links.

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        your Pinboard API token ('username:hex-values') (default: None)
  --ignore REGEX [REGEX ...]
                        ignore links from these hosts (default: None)
  -d, --delete          delete stale links (default: False)
  -e                    equate errors with staleness (default: False)
  --timeout TIMEOUT     HTTP connection timeout (in seconds) (default: 5)
  -v                    enable verbose output (default: False)
  --version             show program's version number and exit
```

You can find your personal Pinboard API token in your [Settings][]. It will
look like `<pinboard-username>:<long-string-of-hex-values>`.

### SSL Certificates

Stale visits each link to verify that it is still active. Because most hosts
use SSL, it's important for your Python environment to have a current set of
SSL certificates. Otherwise, the connection attempt might fail with an error
like `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed`.

For macOS, you can update your certificates by running this command:

    /Applications/Python\ 3.7/Install\ Certificates.command

[latest tarball]: https://github.com/jparise/stale/tarball/master
[Settings]: https://pinboard.in/settings/password
