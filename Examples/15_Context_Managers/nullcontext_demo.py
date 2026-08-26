# nullcontext_demo.py
import sys
import tempfile
from contextlib import AbstractContextManager, nullcontext
from io import StringIO
from pathlib import Path
from typing import IO

def emit(lines: list[str],
         out: IO[str] | Path | None = None) -> None:
    manager: AbstractContextManager[IO[str]]
    match out:
        case Path():
            manager = out.open("w")
        case None:
            manager = nullcontext(sys.stdout)
        case _:
            manager = nullcontext(out)
    with manager as stream:
        for line in lines:
            print(line, file=stream)

emit(["alpha", "beta"])  # Default: stdout, left open
#: alpha
#: beta
buffer = StringIO()
emit(["gamma"], buffer)  # Caller's stream, left open
print(buffer.getvalue().strip(), buffer.closed)
#: gamma False
path = Path(tempfile.gettempdir()) / "emit.txt"
# emit() opened it, so emit() closes it
emit(["delta"], path)
print(path.read_text().strip())
#: delta
path.unlink()
