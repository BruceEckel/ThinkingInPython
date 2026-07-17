#!/usr/bin/env python3
"""Shared paths and book-authoring-convention regexes for the tools/ scripts.

Every tools/*.py script operates on the same repo layout (Chapters/ as the
source of truth, build/examples/ as the extracted, runnable tree) and the
same conventions for reading it: a fenced block's first content line names
the file it extracts to, and a line starting with "#:" marks expected
stdout. A slug starting with "utils/" lands at the tree root's "utils/"
directory instead of a chapter dir, so any chapter can import it.
Centralizing them here means a rename or convention change happens in one
place instead of N.

Behavior lives in tools_repo.py; this module holds only constants. Named
tools_config rather than the shorter "config" so it can never collide with
a book listing of the same name (chapter 24's Singleton demo has one) via
Python's sys.modules cache; see tools_repo.py's docstring for the failure
that would cause.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
CHAPTERS_DIR = ROOT / "Chapters"
PYVER = ROOT / ".python-version"

BUILD_DIR = ROOT / "build"
EXAMPLES_TREE = BUILD_DIR / "examples"
BUILD_SITE_DIR = BUILD_DIR / "site"

NORUN_FILE = TOOLS_DIR / "norun.txt"

# A line marking a listing as unrunnable (GUI, interactive input, infinite
# loop): skip it rather than execute it unattended.
INLINE_NORUN_MARKER = "# extract: no-run"

# A ```lang fence with no leading indent, capturing the language (e.g.
# "python", "py", or "" for a bare ```).
FENCE_RE = re.compile(r"^```(\w+)?\s*$")

# A fence at any indent, opening or closing, with no language capture.
FENCE_ANY_RE = re.compile(r"^\s*```")

# A ```python opener at any indent.
PY_FENCE_RE = re.compile(r"^\s*```python\s*$")

# A block's first content line naming the relative path it extracts to, e.g.
# "# trace.py" or "# mouse/Move.py". A "utils/" prefix (e.g.
# "# utils/display.py") is handled by the caller: it means the file lands
# at the tree root's utils/ directory instead of a chapter dir. A "rust/"
# prefix (e.g. "# rust/fastcount/demo.py") is also handled by the caller
# (extract_examples.py): that slug is excluded entirely, since it is a
# Python caller for a Rust module built by extract_rust.py, not a normal
# book example the main build can run.
PATH_LINE_RE = re.compile(r"^#\s*([\w./\\-]+\.\w+)\s*$")

# A ```rust opener at any indent, for extract_rust.py.
RUST_FENCE_RE = re.compile(r"^\s*```rust\s*$")

# A ```rust block's first content line naming the file it extracts to,
# relative to rust/, e.g. "// fastcount/src/lib.rs". The Rust-comment
# analog of PATH_LINE_RE above.
RUST_PATH_LINE_RE = re.compile(r"^//\s*([\w./\\-]+\.\w+)\s*$")
