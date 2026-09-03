# shrinking.py
from hypothesis import given, settings, strategies

def encode(text: str) -> str:
    return text.encode().hex()

def decode(text: str) -> str:
    return bytes.fromhex(text).decode("latin-1")

@settings(derandomize=True, database=None)
@given(strategies.text())
def roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample

try:
    roundtrip()
except AssertionError as e:
    print(e.__notes__[0])
#: Failing test case: roundtrip(
#:     sample='\x80',
#: )
