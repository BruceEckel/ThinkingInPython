# exercise_6.py
import random
from collections.abc import Iterator

def group_rounds(
    students: list[str], size: int, rng: random.Random
) -> Iterator[list[tuple[str, ...]]]:
    while True:
        pool = list(students)
        rng.shuffle(pool)
        yield [tuple(pool[i:i + size])
               for i in range(0, len(pool), size)]

students = ["Ana", "Bo", "Cy", "Di"]
first = next(group_rounds(students, 2, random.Random(0)))
second = next(group_rounds(students, 2, random.Random(0)))
print(first == second)
#: True
