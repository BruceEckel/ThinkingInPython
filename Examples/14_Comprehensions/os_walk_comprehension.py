# os_walk_comprehension.py
from pathlib import Path

rst_files = [
    dirpath / f
    for dirpath, _, files in Path(".").walk()
    for f in files if f.endswith(".rst")
]
for r in rst_files:
    print(r)
