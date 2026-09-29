# binding_check.py
from typing import Final
from row_check import check

SOURCE: Final[str] = '''
from pathlib import Path

def clear(paths: list[Path]) -> None:
    for dir in paths:
        dir.rmdir()

def load() -> str:
    path = "settings.toml"
    path = Path(path)
    return path.read_text()
'''
report = check({"m": SOURCE})
for name, row in report.rows.items():
    if row:
        print(name, sorted(row))
#: m.clear ['Unknown']
#: m.load ['Unknown']
