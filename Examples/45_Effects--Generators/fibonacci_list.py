# fibonacci_list.py
def fibonacci(n: int) -> list[int]:
    result: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

total = 0
for value in fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
