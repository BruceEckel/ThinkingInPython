# asking_costs.py
DONE = sentinel("DONE")

numbers = iter([1, 2])
print(next(numbers, DONE), next(numbers, DONE),
      next(numbers, DONE))
#: 1 2 DONE
letters = iter("abcd")
# A membership test consumes too:
print("c" in letters, list(letters))
#: True ['d']
