# test_property.py
from hypothesis import given, strategies

def encode(text: str) -> str:
    return text.encode().hex()

def decode(text: str) -> str:
    return bytes.fromhex(text).decode()

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
