# builtin_sum.py
import timeit

numbers = list(range(100_000))

def hand_written() -> int:
    total = 0
    for n in numbers:
        total += n
    return total

assert hand_written() == sum(numbers)
t_loop = timeit.timeit(hand_written, number=50)
t_sum = timeit.timeit(lambda: sum(numbers), number=50)
print(f"sum() at least twice as fast: {t_sum * 2 < t_loop}")
#: sum() at least twice as fast: True
