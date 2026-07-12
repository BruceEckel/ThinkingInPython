# test_property.py
from hypothesis import given, strategies

def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
