# binding_check.py
from typing import Final
from row_check import check, lines

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
for line in lines(check({"m": SOURCE})):
    print(line)
#: m.clear ['Unknown']
#: m.load ['Unknown']
