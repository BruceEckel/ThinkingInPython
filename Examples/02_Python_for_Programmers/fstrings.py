# fstrings.py

name = "Alice"
score = 91.5
print(f"{name} scored {score}")             # Alice scored 91.5
print(f"{name} scored {score:.0f}%")        # Alice scored 92%
print(f"{name!r} has {len(name)} letters")  # 'Alice' has 5 letters
total = 7
print(f"{total = }")                         # total = 7: handy when debugging
