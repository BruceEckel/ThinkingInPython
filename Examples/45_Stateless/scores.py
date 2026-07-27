# scores.py
from typing import Final
from stateless import throws

SCORES: Final[dict[str, int]] = {"alice": 42, "bob": 7}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name.lower()]
