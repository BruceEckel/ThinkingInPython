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

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def pytest_configure(config: pytest.Config) -> None:
    # tools/tools_tests.py runs only these when tools/ is unchanged.
    config.addinivalue_line(
        "markers", "book: reads the book itself, so a chapter edit can "
                   "break it; runs even when tools/ is unchanged")
