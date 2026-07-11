# nullcontext_demo.py
import sys
from contextlib import nullcontext
from io import StringIO
from typing import IO

def emit(lines: list[str], out: IO[str] | None = None) -> None:
    manager = out if out is not None else nullcontext(sys.stdout)
    with manager as stream:
        for line in lines:
            print(line, file=stream)

emit(["alpha", "beta"])   # Defaults to stdout, left open
#: alpha
#: beta
buffer = StringIO()
emit(["gamma"], buffer)   # A managed resource, closed on exit
try:
    print(buffer.read())
except ValueError as e:
    print("ValueError:", e)
#: ValueError: I/O operation on closed file
print(buffer.closed)
#: True
