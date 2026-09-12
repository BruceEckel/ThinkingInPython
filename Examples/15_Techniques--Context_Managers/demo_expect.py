# demo_expect.py
from exceptions import expect

def parse(text: str, *, base: int = 10) -> int:
    return int(text, base)

expect(ValueError, parse, "ff")
#: [ValueError] invalid literal for int() with base 10: 'ff'
expect((ValueError, TypeError), parse, "ff", base=1)
#: [ValueError] int() base must be >= 2 and <= 36, or 0
