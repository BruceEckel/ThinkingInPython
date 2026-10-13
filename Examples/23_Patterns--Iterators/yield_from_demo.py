# yield_from_demo.py
from collections.abc import Sequence
from yield_from import Nested, flatten, flatten_loop

data: Sequence[Nested] = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten(data)))
#: [1, 2, 3, 4, 5, 6, 7]
print(list(flatten_loop(data)) == list(flatten(data)))
#: True
