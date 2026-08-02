# read_score.py
from typing import Final
from stateless import throws

RAW: Final[dict[str, str]] = {"alice": "42", "bob": "seven"}

@throws(KeyError, ValueError)
def read_score(name: str) -> int:
    text = RAW[name.lower()]   # KeyError
    return int(text)           # ValueError
