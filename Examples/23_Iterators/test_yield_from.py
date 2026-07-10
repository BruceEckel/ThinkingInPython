# test_yield_from.py
from collections.abc import Sequence
import pytest
from yield_from import Nested, flatten

@pytest.mark.parametrize("nested, expected", [
    ([1, [2, 3], [4, [5, 6]], 7], [1, 2, 3, 4, 5, 6, 7]),
    ([1, 2, 3], [1, 2, 3]),
])
def test_flatten(
    nested: Sequence[Nested], expected: list[int]
) -> None:
    assert list(flatten(nested)) == expected
