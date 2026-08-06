# param_markers.py

def divide(a, b, /):
    return a / b

print(divide(10, 2))
#: 5.0

def make_user(name, *, admin=False):
    return f"{name} (admin={admin})"

print(make_user("Bob"))
#: Bob (admin=False)
print(make_user("Sue", admin=True))
#: Sue (admin=True)

def tally(label, *values, total=False):
    print(label, values, total)

tally("nums", 1, 2, True)
#: nums (1, 2, True) False
tally("nums", 1, 2, total=True)
#: nums (1, 2) True

try:
    divide(a=10, b=2)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
try:
    make_user("Sue", True)  # type: ignore
except TypeError as e:
    print(e)
#: make_user() takes 1 positional argument but 2 were given
