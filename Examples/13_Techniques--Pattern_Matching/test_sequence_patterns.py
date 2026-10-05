# test_sequence_patterns.py
import pytest
from sequence_patterns import last_of, summarize

@pytest.mark.parametrize("items, expected", [
    ([], "Empty"),
    ([5], "One item: 5"),
    ([3, 4], "Two items: 3, 4"),
    ([1, 2, 3], "1, then 2 more"),
])
def test_summarize_by_length(items: list[int],
                             expected: str) -> None:
    assert summarize(items) == expected

def test_last_of_binds_init_and_last() -> None:
    assert last_of([1, 2, 3, 4]) == ([1, 2, 3], 4)
