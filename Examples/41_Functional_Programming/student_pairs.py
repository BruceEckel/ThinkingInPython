# student_pairs.py
import random
from collections import deque
from collections.abc import Iterator
from itertools import combinations, count, islice

type Student = str
type Group = tuple[Student, ...]
type Round = list[Group]

def round_robin(students: list[Student]) -> Iterator[Round]:
    "Yield groupings; an odd roster gets a triple, not a bye."
    roster: deque[Student | None] = deque(students)
    if len(roster) % 2:
        roster.append(None)  # A placeholder seat for the odd one out
    fixed = roster.popleft()
    for round_number in count():
        seats = [fixed, *roster]
        half = len(seats) // 2
        pairs = [(seats[i], seats[-i - 1]) for i in range(half)]
        groups: list[Group] = []
        leftover: Student | None = None
        for a, b in pairs:
            if a is None or b is None:
                leftover = a if b is None else b
            else:
                groups.append((a, b))
        if leftover is not None:
            idx = random.Random(round_number).randrange(len(groups))
            groups[idx] = (*groups[idx], leftover)
        yield groups
        roster.rotate(1)

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
rounds = list(islice(round_robin(students), len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Bo', 'Gia'), ('Cy', 'Fi', 'Ana'), ('Di', 'Eve')]
#: 1 [('Ana', 'Gia', 'Fi'), ('Bo', 'Eve'), ('Cy', 'Di')]
#: 2 [('Ana', 'Fi', 'Di'), ('Gia', 'Eve'), ('Bo', 'Cy')]

met = [frozenset(pair) for r in rounds for group in r
       for pair in combinations(group, 2)]
possible = set(map(frozenset, combinations(students, 2)))
print(len(set(met)), "of", len(possible), "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(met) - len(set(met)), "repeat meetings")
#: 14 repeat meetings
