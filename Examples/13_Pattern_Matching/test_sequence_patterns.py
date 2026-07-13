# test_sequence_patterns.py
import pytest
from sequence_patterns import summarize

@pytest.mark.parametrize("items, expected", [
    ([], "Empty"),
    ([5], "One item: 5"),
    ([1, 2, 3], "1, then 2 more"),
])
def test_sequence_patterns(items: list[int], expected: str) -> None:
    assert summarize(items) == expected
