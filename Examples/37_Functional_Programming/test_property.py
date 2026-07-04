# test_property.py
from hypothesis import given
from hypothesis import strategies as st

def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

@given(st.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
