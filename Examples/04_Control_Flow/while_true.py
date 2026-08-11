# while_true.py

values = [3, 5, 0, 7]
total = 0
while True:
    value = values.pop(0)
    if value == 0:
        break
    total += value
print(total)
#: 8
