# walrus_filter.py
def cube_if_even(n: int) -> int | None:
    return n ** 3 if n % 2 == 0 else None

data = range(6)
cubes = [
    y for x in data if (y := cube_if_even(x)) is not None
]
print(cubes)
#: [0, 8, 64]
