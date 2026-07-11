# exercise_3.py
mcase = {"a": 10, "b": 34, "A": 7, "Z": 3, "z": 12}

mcase_frequency = {
    k.lower(): mcase.get(k.lower(), 0) + mcase.get(k.upper(), 0)
    for k in mcase
}
print(mcase_frequency)
#: {'a': 17, 'b': 34, 'z': 15}
