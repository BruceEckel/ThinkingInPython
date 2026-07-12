# class_with_defaults.py
from show_redefined import show

class B:
    x: int = 42
    s: str = "Answer"

show(B())
#: [Attributes]
#:   • s: str = 'Answer' [CV]
#:   • x: int = 42 [CV]
#: [Methods]
#:   None
