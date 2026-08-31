# test_catch_subset.py
import pytest
from catch_subset import all_handled, one_unhandled
from stateless import run

@pytest.mark.parametrize("name, expected", [
    ("Alice", "Alice: 42"),
    ("Bob", "Bob: unreadable"),
    ("Carol", "Carol: unknown"),
])
def test_all_handled(name: str, expected: str) -> None:
    assert run(all_handled(name)) == expected

def test_one_unhandled() -> None:
    assert run(one_unhandled("Alice")) == "Alice: 42"
    with pytest.raises(ValueError):
        run(one_unhandled("Bob"))
