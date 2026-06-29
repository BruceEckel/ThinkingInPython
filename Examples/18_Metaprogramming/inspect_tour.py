# inspect_tour.py
import inspect

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    text = f"Hello, {name}"
    return text.upper() if loud else text

print(inspect.signature(greet))
#: (name: str, loud: bool = False) -> str
print(inspect.getdoc(greet))
#: Return a greeting.
print(inspect.isfunction(greet), inspect.isclass(greet))
#: True False
print(list(inspect.signature(greet).parameters))
#: ['name', 'loud']
