# exercise_8.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "exercise_8.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")

# The whole file at once
for line in path.read_text().splitlines():
    print(line)
#: one
#: two
path.unlink()
