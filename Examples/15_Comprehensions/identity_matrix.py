# identity_matrix.py
matrix = [[1 if col == row else 0 for col in range(3)]
          for row in range(3)]
for row in matrix:
    print(row)
#: [1, 0, 0]
#: [0, 1, 0]
#: [0, 0, 1]
