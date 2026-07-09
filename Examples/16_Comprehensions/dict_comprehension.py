# dict_comprehension.py
names = ["Arthur", "Lancelot", "Bedevere", "Ni", "Robin"]

lengths = {name.upper(): len(name) for name in names if len(name) > 3}
print(lengths)
#: {'ARTHUR': 6, 'LANCELOT': 8, 'BEDEVERE': 8, 'ROBIN': 5}
