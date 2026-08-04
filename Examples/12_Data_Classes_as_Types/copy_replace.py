# copy_replace.py
import copy
from datetime import date
from typing import NamedTuple
from stars import Stars

class Size(NamedTuple):
    width: int
    height: int

print(copy.replace(Stars(4), number=9))
#: Stars(number=9)
print(copy.replace(Size(4, 3), height=9))
#: Size(width=4, height=9)
print(copy.replace(date(2026, 8, 4), day=1))
#: 2026-08-01

try:
    copy.replace(Stars(4), number=99)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(99)
