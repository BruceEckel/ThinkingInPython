# identity_matrix.py
from typing import Final

SIZE: Final[int] = 6

matrix = [[1 if col == row else 0 for col in range(SIZE)]
          for row in range(SIZE)]

for row in matrix:
    print(row)
#: [1, 0, 0, 0, 0, 0]
#: [0, 1, 0, 0, 0, 0]
#: [0, 0, 1, 0, 0, 0]
#: [0, 0, 0, 1, 0, 0]
#: [0, 0, 0, 0, 1, 0]
#: [0, 0, 0, 0, 0, 1]
