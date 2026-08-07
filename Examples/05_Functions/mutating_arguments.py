# mutating_arguments.py

def append_all(target, extras):
    target.extend(extras)

mine = [1, 2]
append_all(mine, [3, 4])
print(mine)  # The caller's list changed
#: [1, 2, 3, 4]

def rebind(target):
    target = ["replaced"]  # Rebinds the local name only
    print(target)

rebind(mine)
#: ['replaced']
print(mine)
#: [1, 2, 3, 4]
