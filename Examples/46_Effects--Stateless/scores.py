# scores.py
from typing import Final, reveal_type
from stateless import throws

SCORES: Final[dict[str, int]] = {"Alice": 42, "Bob": 7}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name]

if __name__ == "__main__":
    reveal_type(score)
