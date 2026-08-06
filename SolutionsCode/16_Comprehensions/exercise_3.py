# exercise_3.py
names = ["Arthur", "Lancelot", "Bedevere", "Ni", "Robin", "Galahad"]

lengths = {name.upper(): len(name) for name in names if len(name) > 3}
print(sorted(lengths))
#: ['ARTHUR', 'BEDEVERE', 'GALAHAD', 'LANCELOT', 'ROBIN']
print(lengths["GALAHAD"], "NI" in lengths)
#: 7 False
