#!/usr/bin/env python3
"""Check every external URL in the book for link rot.

Collects each unique ``http(s)://`` URL from the given Markdown files
(default: all of ``Chapters/``), then requests each one and reports any
that fail: connection errors, timeouts, and HTTP status >= 400. A HEAD
request is tried first; servers that reject HEAD (405/403 or an error)
get one GET retry, since many sites treat HEAD differently.

This check is advisory and deliberately not part of ``make verify``.
The network is flaky, sites rate-limit, and a dead external link should
never block a build. Run it occasionally (``make links``) and prune or
update what it reports. Internal cross-references are the job of
``check_anchors.py``, not this script.

Usage:
    python tools/check_links.py                # scan Chapters/
    python tools/check_links.py path ...       # scan specific files/dirs
    python tools/check_links.py --timeout 20   # slow-site tolerance
"""

import argparse
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools_repo import add_paths_arg, md_files

URL_RE = re.compile(r"https?://[^\s)\]>\"'`]+")
# Some hosts refuse requests without a browser-ish User-Agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (ThinkingInPython link check)"}


def find_urls(files: list[Path]) -> dict[str, list[str]]:
    """Map each unique URL to the ``file:line`` places using it.

    Fenced code blocks are skipped: a URL in a listing is example
    data (``https://example.com/...``), not a link a reader follows.
    """
    found: dict[str, list[str]] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        in_code = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            for match in URL_RE.finditer(line):
                url = match.group().rstrip(".,;:")
                found.setdefault(url, []).append(
                    f"{path.name}:{lineno}")
    return found


def probe(url: str, timeout: float) -> str | None:
    """Return a failure description, or None when the URL is fine."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url, method=method, headers=HEADERS)
        try:
            with urllib.request.urlopen(
                    request, timeout=timeout) as response:
                if response.status < 400:
                    return None
                failure = f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            failure = f"HTTP {e.code}"
        except Exception as e:  # URLError, timeout, SSL, ...
            failure = type(e).__name__
    return failure


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="seconds per request (default: 10)")
    args = ap.parse_args(argv)

    urls = find_urls(md_files(args.paths))
    print(f"Checking {len(urls)} unique external links...")
    with ThreadPoolExecutor(max_workers=16) as pool:
        failures = {
            url: outcome
            for url, outcome in zip(
                urls, pool.map(
                    lambda u: probe(u, args.timeout), urls))
            if outcome is not None
        }
    for url in sorted(failures):
        print(f"  ! {failures[url]:<22} {url}")
        for place in urls[url][:3]:
            print(f"      {place}")
    ok = len(urls) - len(failures)
    print(f"{ok} ok, {len(failures)} failing.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
