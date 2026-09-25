# test_composing.py
import pytest
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind

@pytest.mark.parametrize("i", range(5))
def test_manual_and_bind_agree(i: int) -> None:
    assert composed_manual(i) == composed_bind(i)
