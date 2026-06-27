# test_composing.py
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind

def test_manual_and_bind_agree() -> None:
    for i in range(5):
        assert composed_manual(i) == composed_bind(i)
