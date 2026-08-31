# flatten.py
rows = [[1, 2], [3, 4], [5]]
print([x for row in rows for x in row])
#: [1, 2, 3, 4, 5]
