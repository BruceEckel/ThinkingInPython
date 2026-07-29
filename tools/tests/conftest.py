"""Make the tools/ scripts importable from the tests beside them.

The scripts in tools/ are entry points run as ``python tools/foo.py``,
not an installed package, so they import their siblings by bare name
(``from tools_config import ROOT``) and rely on Python putting the
script's own directory on sys.path. A test file two directories down
gets no such help, so each test used to open with its own copy of the
insert below. pytest imports this file before collecting anything in
this directory, so one copy here covers every test.

Deliberately not done by adding tools/ to pyproject.toml's
``pythonpath``: that setting also applies when pytest runs the book's
own examples, which would put the tooling modules on sys.path for
every listing and reintroduce the shadowing that the tools_* prefix
exists to prevent (see tools_repo.py's docstring).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
