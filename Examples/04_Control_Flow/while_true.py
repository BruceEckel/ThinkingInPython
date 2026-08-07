# while_true.py

values = iter([3, 5, 0, 7])
total = 0
while True:
    value = next(values)
    if value == 0:
        break
    total += value
print(total)
#: 8
