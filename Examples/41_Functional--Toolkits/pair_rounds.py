# pair_rounds.py
from itertools import combinations, islice
from student_groups import group_rounds

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia",
            "Hal"]
rounds = list(islice(group_rounds(students, 2),
                     len(students) - 1))
for i, grouping in enumerate(rounds[:3]):
    print(i, *map("-".join, grouping))
#: 0 Gia-Eve Hal-Bo Di-Fi Ana-Cy
#: 1 Gia-Bo Hal-Ana Cy-Eve Di-Fi
#: 2 Cy-Fi Hal-Eve Bo-Di Ana-Gia

meetings = [*map(frozenset, combinations(group, 2))
            for r in rounds for group in r]
possible = set(map(frozenset, combinations(students, 2)))
distinct = set(meetings)
print(len(distinct), "of", len(possible),
      "pairs met at least once")
#: 26 of 28 pairs met at least once
print(len(meetings) - len(distinct), "repeat meetings")
#: 2 repeat meetings
