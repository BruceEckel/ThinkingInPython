# param_markers.py
# `/` ends the positional-only parameters.
# `*` begins the keyword-only parameters.

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
