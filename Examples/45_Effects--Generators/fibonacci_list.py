# fibonacci_list.py
def fibonacci(n: int) -> list[int]:
    values: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        print(f"computed {a}")
        values.append(a)
        a, b = b, a + b
    return values

total = 0
for value in fibonacci(7):
    total += value
    print(f"{value=} {total=}")
    if total > 10:
        break
#: computed 0
#: computed 1
#: computed 1
#: computed 2
#: computed 3
#: computed 5
#: computed 8
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
