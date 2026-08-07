# all_markers.py

def f(a, /, b, *args, c, **kwargs):
    print(a, b, args, c, kwargs)

f(1, 2, 3, 4, c=5, d=6)
#: 1 2 (3, 4) 5 {'d': 6}
