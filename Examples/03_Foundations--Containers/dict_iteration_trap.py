# dict_iteration_trap.py

d = {"a": 1, "b": 2, "c": 3}
try:
    for k in d:
        del d[k]
except RuntimeError as e:
    print(e)
#: dictionary changed size during iteration
