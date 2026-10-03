# comprehension_side_effects.py
wasted = [print(n) for n in [1, 2, 3]]
#: 1
#: 2
#: 3
print(wasted)
#: [None, None, None]
