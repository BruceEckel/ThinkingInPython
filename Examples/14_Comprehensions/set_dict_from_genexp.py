# set_dict_from_genexp.py
words = ["pol", "parrot", "pining", "fjord", "ex"]

lengths = set(len(w) for w in words)
print(sorted(lengths))
# [2, 3, 5, 6]

initials = dict((w, w[0]) for w in words)
print(initials)
# {'pol': 'p', 'parrot': 'p', 'pining': 'p', 'fjord': 'f', 'ex': 'e'}
