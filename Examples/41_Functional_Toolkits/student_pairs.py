# student_pairs.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()
    rng = random.Random(seed)

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
rounds = list(islice(group_rounds(students, 2),
                     len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
#: 1 [('Di', 'Bo', 'Eve'), ('Cy', 'Ana'), ('Gia', 'Fi')]
#: 2 [('Eve', 'Fi', 'Ana'), ('Bo', 'Gia'), ('Cy', 'Di')]

meetings = [frozenset(pair) for r in rounds for group in r
            for pair in combinations(group, 2)]
possible = set(map(frozenset, combinations(students, 2)))
distinct = set(meetings)
print(len(distinct), "of", len(possible),
      "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(meetings) - len(distinct), "repeat meetings")
#: 14 repeat meetings

trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]

# Fewer than `size`
print(next(group_rounds(["Ana", "Bo"], 5)))
#: [('Ana', 'Bo')]
