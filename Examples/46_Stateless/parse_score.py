# parse_score.py
from typing import Final
from stateless import throws

RAW: Final[dict[str, str]] = {"alice": "42", "bob": "seven"}

@throws(KeyError, ValueError)
def parse_score(name: str) -> int:
    return int(RAW[name.lower()])
