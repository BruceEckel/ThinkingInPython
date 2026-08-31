# comprehension_side_effects.py
wasted = [print(n) for n in [1, 2, 3]]
print(wasted)
#: 1
#: 2
#: 3
#: [None, None, None]
