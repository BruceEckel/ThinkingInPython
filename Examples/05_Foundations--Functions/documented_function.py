# documented_function.py

def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"

print(greet("Ann"))
#: Hello, Ann!
print(greet.__doc__)
#: Return a greeting for name.
