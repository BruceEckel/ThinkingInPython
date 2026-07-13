# path_walk_comprehension.py
import tempfile
from pathlib import Path

# Build a small tree to walk: two .py files and one to skip
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "pkg").mkdir()
    for name in ("main.py", "pkg/util.py", "pkg/notes.txt"):
        (root / name).write_text("")
    py_paths = [
        (dirpath / f).relative_to(root).as_posix()
        for dirpath, _, files in root.walk()
        for f in files if f.endswith(".py")
    ]

for path in sorted(py_paths):  # Sorted for stable output
    print(path)
#: main.py
#: pkg/util.py
