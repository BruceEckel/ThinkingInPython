# class_with_defaults.py
from comparison import show

class B:
    x: int = 42
    s: str = "Answer"

show(B())
#: [Attributes]
#:   • s: str = 'Answer' [CV]
#:   • x: int = 42 [CV]
#: [Methods]
#:   None

print(B.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
