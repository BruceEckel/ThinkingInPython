# context_manager.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "demo.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")  # f.close() happens automatically

with path.open() as f:
    for line in f:
        print(line.strip())

path.unlink()  # Delete the file
