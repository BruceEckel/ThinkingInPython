# trio_rounds.py
from itertools import islice
from student_pairs import group_rounds

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]
