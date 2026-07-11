# unpacking.py

def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
#: 1 2 3
f(*(4, 5, 6))
#: 4 5 6
# ** unpacks a dictionary into keyword arguments:
d = {"a": 3.14, "b": 1.62, "c": 2.72}
f(**d)
#: 3.14 1.62 2.72

def report(label, *values, **options):
    print(label, values, options)

nums = (1, 2, 3)
opts = {"color": "red", "size": 10}
report("point", *nums, **opts)
#: point (1, 2, 3) {'color': 'red', 'size': 10}
