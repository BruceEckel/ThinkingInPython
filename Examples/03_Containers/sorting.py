# sorting.py

words = ["pear", "Fig", "apple"]
print(sorted(words))  # A new list; words is untouched
#: ['Fig', 'apple', 'pear']
print(words)
#: ['pear', 'Fig', 'apple']
print(words.sort())  # Sorts in place and returns None
#: None
print(words)
#: ['Fig', 'apple', 'pear']
print(sorted(words, reverse=True))
#: ['pear', 'apple', 'Fig']
