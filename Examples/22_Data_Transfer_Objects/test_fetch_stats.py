# test_fetch_stats.py
from fetch_stats import Stats, summarize

def test_summarize_returns_named_fields() -> None:
    s = summarize([2.0, 4.0, 6.0])
    assert s == Stats(4.0, 3)
    assert s == (4.0, 3)  # A NamedTuple is still a tuple
