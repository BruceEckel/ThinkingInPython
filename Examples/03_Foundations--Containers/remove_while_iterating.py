# remove_while_iterating.py

xs = [1, 2, 3, 4]
for x in xs:
    print(x)
    xs.remove(x)
#: 1
#: 3
print(xs)
#: [2, 4]
