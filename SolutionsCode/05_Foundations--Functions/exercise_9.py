# exercise_9.py
def clear_by_assignment(target):
    target = []  # Rebinds the local name
    print(target)

def clear_by_method(target):
    target.clear()  # Changes the caller's list

mine = [1, 2, 3]
clear_by_assignment(mine)
#: []
print(mine)
#: [1, 2, 3]
clear_by_method(mine)
print(mine)
#: []
