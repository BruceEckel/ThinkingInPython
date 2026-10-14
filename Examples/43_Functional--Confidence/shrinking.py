# shrinking.py
from codec import encode
from hypothesis import given, settings, strategies

def decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode("latin-1")

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
print(repr(decode(encode("\x80"))))  # [1]
#: 'Â\x80'
