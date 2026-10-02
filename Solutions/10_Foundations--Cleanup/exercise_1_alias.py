# exercise_1_alias.py
counters = [1, 2, 3]
other = counters  # A second name for the same list
counters = []  # Rebinding: 'other' still sees the old list
print(other)
#: [1, 2, 3]
counters = [1, 2, 3]
other = counters
counters.clear()  # Clearing: 'other' sees the emptied list
print(other)
#: []
