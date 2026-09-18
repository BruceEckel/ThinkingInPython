# effect_table.py
from fnmatch import fnmatchcase
from typing import Final
from effect_names import (
    Clock,
    Console,
    Environment,
    FileSystem,
    Network,
    Process,
    Random,
    Unknown,
)

type Row = frozenset[str]
type Table = dict[str, Row]

def names(*effects: type) -> Row:
    return frozenset(e.__name__ for e in effects)

PURE: Final[Row] = names()
UNKNOWN: Final[Row] = names(Unknown)
STDLIB: Final[Table] = {
    "builtins.print": names(Console),
    "builtins.input": names(Console),
    "builtins.open": names(FileSystem),
    "builtins.eval": UNKNOWN,
    "builtins.exec": UNKNOWN,
    "builtins.*": PURE,
    "pathlib.Path": PURE,
    "pathlib.Path.with_*": PURE,
    "pathlib.Path.*": names(FileSystem),
    "time.time": names(Clock),
    "time.sleep": names(Clock),
    "time.perf_counter": names(Clock),
    "datetime.datetime.now": names(Clock),
    "random.*": names(Random),
    "os.environ.*": names(Environment),
    "os.getenv": names(Environment),
    "os.path.join": PURE,
    "os.*": names(FileSystem),
    "socket.*": names(Network),
    "urllib.request.*": names(Network),
    "subprocess.*": names(Process),
    "ast.*": PURE,
    "fnmatch.*": PURE,
    "itertools.*": PURE,
    "functools.*": PURE,
    "math.*": PURE,
    "typing.*": PURE,
}

def lookup(name: str, table: Table) -> Row:
    for pattern, row in table.items():
        if fnmatchcase(name, pattern):
            return row
    return UNKNOWN
