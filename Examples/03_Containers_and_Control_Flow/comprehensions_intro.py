# comprehensions_intro.py

squares = [n * n for n in range(5)]           # list comprehension
print(squares)                                # [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # with a filter
print(evens)                                  # [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}    # dict comprehension
print(lengths)                                # {'a': 1, 'bb': 2}
