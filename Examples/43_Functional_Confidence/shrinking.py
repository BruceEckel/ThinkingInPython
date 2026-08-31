# shrinking.py
from hypothesis import given, settings, strategies

def encode(text: str) -> str:
    return text.replace(" ", "_")

def decode(text: str) -> str:
    return text.replace("_", " ")

@settings(derandomize=True, database=None)
@given(strategies.text())
def roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample

try:
    roundtrip()
except AssertionError as e:
    print(e.__notes__[0])
#: Failing test case: roundtrip(
#:     sample='_',
#: )
