# test_stars.py
import pytest
from stars import Stars, f1, f2
from validation import TypeFailure

def test_legal_stars() -> None:
    assert Stars(1).number == 1
    assert Stars(10).number == 10

@pytest.mark.parametrize("n", [0, 11, -1, 100])
def test_illegal_stars_rejected(n: int) -> None:
    with pytest.raises(TypeFailure):
        Stars(n)

def test_transformations_return_legal_values() -> None:
    assert f1(Stars(2)) == Stars(7)
    assert f2(Stars(2)) == Stars(10)

def test_illegal_result_is_rejected() -> None:
    with pytest.raises(TypeFailure, match=r"Stars\(20\)"):
        f2(Stars(4))
