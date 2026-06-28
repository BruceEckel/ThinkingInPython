# unpacking.py
# Turn a sequence into positional arguments with *.
def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
#: 1 2 3
f(*(1, 2, 3))
#: 1 2 3
# ** unpacks a dictionary into keyword arguments:
d = {"a": 10, "b": 20, "c": 30}
f(**d)
#: 10 20 30

# Collecting and unpacking are inverses, so you can collect
# arguments in one function and forward them unchanged:
def report(label, *values, **options):
    print(label, values, options)

nums = (1, 2, 3)
opts = {"color": "red", "size": 10}
report("point", *nums, **opts)
#: point (1, 2, 3) {'color': 'red', 'size': 10}
