"""Make the tools package importable from the tests inside it.

The tools are run as ``python -m tools.foo`` from the repository root,
which puts the root on sys.path so ``from tools.config import ROOT``
resolves. pytest gives a test file two directories down no such help:
it inserts the test's own directory, not the root. This file inserts
the root once, before pytest collects anything here, so no test needs
its own copy.

Deliberately not done by adding "." to pyproject.toml's ``pythonpath``:
that setting also applies when pytest runs the book's own examples, and
the root should stay off the path there so a listing sees only its
chapter directory and utils/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
