# exercise_2.py
from typing import Final

SIZE: Final[int] = 6

matrix = [[2 if col == row else 0 for col in range(SIZE)]
          for row in range(SIZE)]
for row in matrix:
    print(row)
#: [2, 0, 0, 0, 0, 0]
#: [0, 2, 0, 0, 0, 0]
#: [0, 0, 2, 0, 0, 0]
#: [0, 0, 0, 2, 0, 0]
#: [0, 0, 0, 0, 2, 0]
#: [0, 0, 0, 0, 0, 2]
