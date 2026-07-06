# test_yield_from.py
from yield_from import flatten

def test_flatten_nested_lists() -> None:
    result = list(flatten([1, [2, 3], [4, [5, 6]], 7]))
    assert result == [1, 2, 3, 4, 5, 6, 7]

def test_flatten_no_nesting() -> None:
    assert list(flatten([1, 2, 3])) == [1, 2, 3]
