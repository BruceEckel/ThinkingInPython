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
print(f"{total=}")
#: total=20
