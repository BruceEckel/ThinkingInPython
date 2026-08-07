# list_traps.py

grid = [[0]] * 3  # Three names for one inner list
grid[0][0] = 1
print(grid)
#: [[1], [1], [1]]
grid = [[0] for _ in range(3)]  # Three separate lists
grid[0][0] = 1
print(grid)
#: [[1], [0], [0]]
