# exercise_5.py
import inspect

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    text = f"Hello, {name}"
    return text.upper() if loud else text

def describe(func) -> None:
    doc = inspect.getdoc(func)
    sig = inspect.signature(func)
    print(func.__name__, sig, doc or "(no docstring)")

describe(greet)
#: greet (name: str, loud: bool = False) -> str Return a greeting.
describe(lambda x: x * 2)
#: <lambda> (x) (no docstring)
