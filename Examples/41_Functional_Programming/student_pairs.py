# student_pairs.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice

type Student = str
type Group = tuple[Student, ...]
type Round = list[Group]

def group_rounds(
    students: list[Student], size: int, seed: int = 0
) -> Iterator[Round]:
    "Yield groupings of `size`; greedily keeps repeats to a minimum."
    history: Counter[frozenset[Student]] = Counter()
    rng = random.Random(seed)
    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[Student]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                closest = min(pool, key=lambda c: sum(
                    history[frozenset((m, c))] for m in group))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        for extra in pool:  # Too few left for a full group of `size`
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
rounds = list(islice(group_rounds(students, 2), len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
#: 1 [('Di', 'Bo', 'Eve'), ('Cy', 'Ana'), ('Gia', 'Fi')]
#: 2 [('Eve', 'Fi', 'Ana'), ('Bo', 'Gia'), ('Cy', 'Di')]

met = [frozenset(pair) for r in rounds for group in r
       for pair in combinations(group, 2)]
possible = set(map(frozenset, combinations(students, 2)))
print(len(set(met)), "of", len(possible), "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(met) - len(set(met)), "repeat meetings")
#: 14 repeat meetings

trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]
