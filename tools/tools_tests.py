#!/usr/bin/env python
"""Run the tools' own tests (tools/tests), skipping them when tools/ is unchanged.

The gate's first step. The suite tests the tools, so while no file under
``tools/`` (nor ``pyproject.toml`` or ``uv.lock``) has changed since it
last passed, a rerun can only repeat the verdict. Then only the tests
marked ``book`` run: the few that read the book itself, which a chapter
edit can break with the tools untouched. ``tools/skip_stamps.py`` holds
the digest and the stamp, and explains the policy.

Usage:
    python -m tools.tools_tests [pytest args]      # skip when unchanged
    python -m tools.tools_tests --always [args]    # full suite, refresh stamp

``TIP_FULL=1`` in the environment acts as ``--always``.
"""

import subprocess
import sys

from tools.config import ROOT
from tools.skip_stamps import (
    forced_full, record_tools_tests, tools_digest, tools_tests_current)

SUITE = "tools/tests"


def pytest(*args: str) -> int:
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args, SUITE], cwd=ROOT).returncode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    always = "--always" in args
    if always:
        args.remove("--always")
    # Hash before running, so an edit made while the suite runs is not
    # stamped as tested.
    digest = tools_digest()
    if not always and not forced_full() and tools_tests_current(digest):
        print("tools/tests: tools/ unchanged since the last pass; "
              "running only the tests marked `book` "
              "(tip tools-test runs them all)")
        code = pytest("-q", "-m", "book", *args)
        # 5: every test deselected, which is fine here.
        return 0 if code == 5 else code
    code = pytest(*args)
    if code == 0:
        record_tools_tests(digest)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
