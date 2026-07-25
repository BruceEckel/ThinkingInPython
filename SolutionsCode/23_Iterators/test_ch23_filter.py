# test_ch23_filter.py
from collections.abc import Iterator
from itertools import count
from typing import Final
import pytest

LIMIT: Final[int] = 1000

class Tripwire(Exception):
    pass

def counter(limit: int) -> Iterator[int]:
    for n in count(1):
        if n > limit:
            raise Tripwire(f"pulled {limit} values and kept asking")
        yield n

def test_filter_skips_but_never_stops() -> None:
    with pytest.raises(Tripwire):
        list(filter(lambda n: n < 3, counter(LIMIT)))
