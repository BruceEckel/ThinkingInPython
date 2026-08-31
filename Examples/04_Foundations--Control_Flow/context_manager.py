# context_manager.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "demo.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")  # Automatic f.close()

with path.open() as f:
    for line in f:
        print(line.strip())
#: one
#: two
try:
    with path.open("w") as f:
        f.write("partial")
        raise RuntimeError("failed midway")
except RuntimeError as e:
    print(e)
#: failed midway
print("closed:", f.closed)
#: closed: True
path.unlink()  # Delete the file
