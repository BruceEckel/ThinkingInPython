# exercise_5.py
xs = [10, 20, 30, 40, 50]
print(xs[-2:])  # The last two items
#: [40, 50]
print(xs[1:-1])  # Everything but the first and last
#: [20, 30, 40]
print(xs[1:4][::-1])  # The middle three, reversed
#: [40, 30, 20]
print(xs[3:0:-1])  # The same three, in one slice
#: [40, 30, 20]
