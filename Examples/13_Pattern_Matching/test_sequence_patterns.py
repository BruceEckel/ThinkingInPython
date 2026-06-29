# test_sequence_patterns.py
from sequence_patterns import summarize

def test_sequence_patterns() -> None:
    assert summarize([]) == "Empty"
    assert summarize([5]) == "One item: 5"
    assert summarize([1, 2, 3]) == "1, then 2 more"
