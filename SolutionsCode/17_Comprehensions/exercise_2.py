# exercise_2.py
matrix = [[2 if col == row else 0 for col in range(3)]
          for row in range(3)]
for row in matrix:
    print(row)
#: [2, 0, 0]
#: [0, 2, 0]
#: [0, 0, 2]
