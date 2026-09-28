# pair_rounds.py
from itertools import combinations, islice
from student_pairs import group_rounds

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
rounds = list(islice(group_rounds(students, 2),
                     len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
#: 1 [('Di', 'Bo', 'Eve'), ('Cy', 'Ana'), ('Gia', 'Fi')]
#: 2 [('Eve', 'Fi', 'Ana'), ('Bo', 'Gia'), ('Cy', 'Di')]

meetings = [*map(frozenset, combinations(group, 2))
            for r in rounds for group in r]
possible = set(map(frozenset, combinations(students, 2)))
distinct = set(meetings)
print(len(distinct), "of", len(possible),
      "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(meetings) - len(distinct), "repeat meetings")
#: 14 repeat meetings
