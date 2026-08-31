# exercise_5.py
def show(n: int) -> str:
    line = f"item {n}"
    print(line)
    return line

lines = [show(n) for n in [1, 2, 3]]
#: item 1
#: item 2
#: item 3
print(lines)
#: ['item 1', 'item 2', 'item 3']

for n in [1, 2, 3]:  # Printing alone stays a loop
    print(f"item {n}")
#: item 1
#: item 2
#: item 3
