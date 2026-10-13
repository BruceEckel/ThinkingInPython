# test_property.py
from codec import decode, encode
from hypothesis import given, strategies

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
