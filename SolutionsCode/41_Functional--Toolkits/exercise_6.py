# exercise_6.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, rng: random.Random
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()

    def met(group: list[str], candidate: str) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[str]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                closest = min(pool,
                              key=lambda c: met(group, c))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        # Too few left for a full group of `size`
        for extra in pool:
            roomiest = min(groups,
                           key=lambda g: met(g, extra))
            roomiest.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
first = next(group_rounds(students, 2, random.Random(0)))
second = next(group_rounds(students, 2, random.Random(0)))
print(first == second)
#: True
print(first)
#: [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
