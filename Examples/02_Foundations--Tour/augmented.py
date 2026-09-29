# augmented.py

total = 0
total += 5  # Augmented assignment, like other languages
print(total)
#: 5
items = [1, 2]
alias = items
items += [3]  # In place, so alias sees it
print(alias)
#: [1, 2, 3]
items = items + [4]  # A new list, alias keeps the old one
print(alias, items)
#: [1, 2, 3] [1, 2, 3, 4]
