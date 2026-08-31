# alias_default.py

type Pair[T = int] = tuple[T, T]

def is_origin(point: Pair) -> bool:  # Pair means Pair[int]
    return point == (0, 0)

print(is_origin((0, 0)))
#: True
