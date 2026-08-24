#!/usr/bin/env python3
"""Publish a GitHub release whose assets are the fresh PDF and EPUBs.

`make release VERSION=1.0` lands here. The release's uploaded assets
are exactly three files, ThinkingInPython.pdf plus the two EPUB
variants (ThinkingInPython-color.epub for backlit readers,
ThinkingInPython-eink.epub with bolding instead of color), all rebuilt
from the current Markdown by this run, never taken from a stale
build/ tree. (GitHub itself always adds "Source code" archive links
to a release page; those are GitHub's, not uploads.)

The order is preflight, verify, build, publish, with the cheap checks
first so a doomed run dies before the expensive gate:

1. Preflight: a VERSION was given and makes a sane tag; `gh` is
   installed and authenticated; the working tree is clean; HEAD is a
   branch whose tip matches origin (a release tag must point at a
   commit that is actually on GitHub, holding the book that built the
   assets); and the tag does not already exist, locally or on origin.
2. `make verify`: the full gate, so a book that fails it can never
   ship. verify's fixers (line endings, `#:` markers, sync) can
   rewrite tracked files; if that happens the tree is no longer the
   pushed commit, so the run stops and asks for a review-commit-push
   before trying again.
3. Build the PDF and EPUBs (in-process, the equivalent of `make pdf`
   and `make epub` plus a `--release` stamp): both builders wipe
   their output directory and rebuild from the Markdown, which is
   what makes the assets fresh, and both stamp their title page with
   the release number and today's date ("Release 1.0 · August 23,
   2026") so the reader can tell which release they hold.
4. `gh release create v<VERSION> <pdf> <epubs>`: creates the tag on
   origin at the branch tip and uploads the three assets. gh prints
   the release URL on success.

The tag is the VERSION prefixed with "v" (a bare "v1.0" is accepted
as-is), the conventional GitHub form. Deleting a bad release is a
manual, deliberate act: `gh release delete v1.0 --cleanup-tag`.

Usage:
    python tools/release.py 1.0     # normally via `make release VERSION=1.0`

Requires `git` and an authenticated `gh` on PATH, plus everything
`make verify`, `make pdf`, and `make epub` need.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import build_epub
import build_pdf
from tools_config import BUILD_EPUB_DIR, BUILD_PDF_DIR, ROOT
from tools_repo import run_echoed

# A tag is the version with a "v" prefix; the version itself stays to
# letters, digits, dots, hyphens, underscores. Stricter than git's own
# rules on purpose: it keeps shell quoting and URL escaping out of the
# picture, and every plausible book version ("1.0", "2.0-beta1") fits.
# \Z rather than $: $ would accept a trailing newline.
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\Z")

# Network git/gh calls get a real timeout; local ones stay snappy.
LOCAL_TIMEOUT = 30
REMOTE_TIMEOUT = 120


def tag_for(version: str) -> str:
    """The git tag for a version: "1.0" -> "v1.0", "v1.0" kept as-is."""
    return version if version.startswith("v") else f"v{version}"


def title_for(version: str) -> str:
    """The release title: the book's name plus the bare version number."""
    return f"Thinking in Python {version.removeprefix('v')}"


def git(*args: str, timeout: float = LOCAL_TIMEOUT) -> str:
    """One git command's stdout, stripped. Exits the run on failure."""
    proc = subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", timeout=timeout, cwd=ROOT)
    if proc.returncode != 0:
        sys.exit(f"error: git {' '.join(args)} failed:\n{proc.stderr}")
    return proc.stdout.strip()


def check_gh() -> None:
    if shutil.which("gh") is None:
        sys.exit("error: gh (the GitHub CLI) not found on PATH. "
                 "Install it: winget install GitHub.cli / "
                 "https://cli.github.com")
    proc = subprocess.run(["gh", "auth", "status"], capture_output=True,
                          text=True, encoding="utf-8",
                          timeout=REMOTE_TIMEOUT)
    if proc.returncode != 0:
        sys.exit("error: gh is not authenticated. Run: gh auth login")


def working_tree_dirty() -> str:
    """`git status --porcelain`, empty when the tree is clean."""
    return git("status", "--porcelain")


def preflight(tag: str) -> str:
    """Every check that should fail before the gate spends minutes.

    Returns the branch to release from.
    """
    check_gh()

    dirty = working_tree_dirty()
    if dirty:
        sys.exit("error: the working tree has uncommitted changes; a "
                 "release must be built from a pushed commit:\n"
                 f"{dirty}")

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "HEAD":
        sys.exit("error: detached HEAD; check out a branch to release.")
    head = git("rev-parse", "HEAD")
    remote = git("ls-remote", "origin", f"refs/heads/{branch}",
                 timeout=REMOTE_TIMEOUT)
    if not remote:
        sys.exit(f"error: branch {branch} does not exist on origin; "
                 "push it first.")
    if remote.split()[0] != head:
        sys.exit(f"error: local {branch} ({head[:12]}) does not match "
                 f"origin/{branch} ({remote.split()[0][:12]}); push or "
                 "pull first. The release tag must point at the pushed "
                 "commit the assets were built from.")

    if git("tag", "--list", tag):
        sys.exit(f"error: tag {tag} already exists locally. Pick a new "
                 f"VERSION, or delete the old release deliberately: "
                 f"gh release delete {tag} --cleanup-tag")
    if git("ls-remote", "origin", f"refs/tags/{tag}",
           timeout=REMOTE_TIMEOUT):
        sys.exit(f"error: tag {tag} already exists on origin. Pick a "
                 "new VERSION.")
    return branch


def make(target: str) -> None:
    """Run one make target, aborting the release if it fails."""
    if not run_echoed(["make", target]):
        sys.exit(f"error: make {target} failed; nothing was released.")


def build_assets(version: str) -> list[Path]:
    """Rebuild the PDF and both EPUBs fresh, stamped with the release.

    In-process calls rather than `make pdf`/`make epub`: the make
    targets have no way to carry the release stamp, and the builders
    are already imported. Each stamps its title page with
    `build_epub.release_line()` ("Release 1.0 · August 23, 2026").
    A nonzero status (a missing image, an unresolved link) aborts the
    release: a warning a reader would see must not ship.
    """
    print(f"\n--- Building the PDF (release {version}) ---")
    if build_pdf.build(BUILD_PDF_DIR, release=version) != 0:
        sys.exit("error: the PDF build reported problems; nothing "
                 "was released.")
    print(f"\n--- Building the EPUBs (release {version}) ---")
    if build_epub.build(BUILD_EPUB_DIR, release=version) != 0:
        sys.exit("error: the EPUB build reported problems; nothing "
                 "was released.")
    assets = [BUILD_PDF_DIR / build_pdf.PDF_NAME,
              *(BUILD_EPUB_DIR / build_epub.epub_name(v)
                for v in build_epub.VARIANTS)]
    for asset in assets:
        if not asset.is_file() or asset.stat().st_size == 0:
            sys.exit(f"error: expected asset missing after the build: "
                     f"{asset}")
    return assets


def publish(tag: str, version: str, branch: str,
            assets: list[Path]) -> None:
    head = git("rev-parse", "HEAD")
    notes = ("The complete book as PDF and EPUB.\n\n"
             "Two EPUBs: `-color` has color syntax highlighting for "
             "backlit readers (phone/tablet apps); `-eink` marks "
             "code with bolding instead, for e-ink devices where "
             "color is invisible.\n\n"
             f"Built from `{branch}` @ {head[:12]}.")
    command = ["gh", "release", "create", tag,
               "--target", branch,
               "--title", title_for(version),
               "--notes", notes,
               *[str(a) for a in assets]]
    if not run_echoed(command):
        sys.exit("error: gh release create failed. If the tag was "
                 f"created anyway, clean up with: gh release delete "
                 f"{tag} --cleanup-tag")


def release(version: str) -> int:
    if not VERSION_RE.match(version):
        sys.exit(f"error: {version!r} is not a usable VERSION "
                 "(letters, digits, dots, hyphens, underscores).")
    tag = tag_for(version)
    branch = preflight(tag)

    make("verify")
    dirty = working_tree_dirty()
    if dirty:
        sys.exit("error: `make verify` rewrote tracked files (its "
                 "fixers self-heal markers, line endings, and synced "
                 "trees), so the tree no longer matches the pushed "
                 "commit. Review the diff, commit, push, and run "
                 f"`make release VERSION={version}` again:\n{dirty}")

    assets = build_assets(version.removeprefix("v"))
    publish(tag, version, branch, assets)
    print(f"\nReleased {title_for(version)} as {tag}: "
          f"{', '.join(a.name for a in assets)}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", nargs="?",
                    help='the release version, e.g. 1.0 (tagged as "v1.0")')
    args = ap.parse_args(argv)
    if not args.version:
        sys.exit("error: no version given. Run as: "
                 "make release VERSION=1.0")
    os.chdir(ROOT)
    return release(args.version)


if __name__ == "__main__":
    raise SystemExit(main())
