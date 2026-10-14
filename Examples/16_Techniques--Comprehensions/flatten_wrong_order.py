# flatten_wrong_order.py
rows = [[1, 2], [3, 4], [5]]
try:
    print([x for x in row for row in rows])  # type: ignore
except NameError as e:
    print(e)
#: name 'row' is not defined

row = [7, 8]
print([x for x in row for row in rows])
#: [7, 7, 7, 8, 8, 8]
