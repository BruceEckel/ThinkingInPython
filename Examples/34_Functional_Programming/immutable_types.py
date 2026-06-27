# immutable_types.py
from collections.abc import Sequence
from typing import Final

# Final marks a name the checker won't let you rebind:
MAX_SIZE: Final = 100

# Sequence is read-only: no append, no item assignment:
def total(values: Sequence[int]) -> int:
    return sum(values)

print(MAX_SIZE, total([1, 2, 3]))
## 100 6
