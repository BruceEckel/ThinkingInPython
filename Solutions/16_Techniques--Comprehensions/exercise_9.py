# exercise_9.py
calls: list[int] = []

def cube_if_even(n: int) -> int | None:
    calls.append(n)
    return n ** 3 if n % 2 == 0 else None

data = range(6)
cubes = [
    y for x in data if (y := cube_if_even(x)) is not None
]
print(cubes, len(calls))
#: [0, 8, 64] 6
calls.clear()
again = [
    cube_if_even(x) for x in data
    if cube_if_even(x) is not None
]
print(again, len(calls))
#: [0, 8, 64] 9
print(calls)
#: [0, 0, 1, 2, 2, 3, 4, 4, 5]
