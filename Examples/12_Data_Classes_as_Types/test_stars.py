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

def test_transformation_can_produce_illegal_value() -> None:
    # f2 multiplies, so its result can be outside the legal set.
    # Construction of the returned Stars catches it: no illegal
    # Stars can ever exist.
    with pytest.raises(TypeFailure):
        f2(Stars(4))  # 4 * 5 = 20
