# class_var.py
from typing import ClassVar
from display import display_object

class Tally:
    total: ClassVar[int] = 0  # A single shared value
    label: str  # Declared, not yet assigned

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

display_object(Tally)
#: === Tally ===
#: [Attributes]
#:   • total: typing.ClassVar[int] = 0
#: [Methods]
#:   None
a = Tally("a")
display_object(a)
#: === Tally ===
#: [Attributes]
#:   • label: str = 'a'
#:   • total: typing.ClassVar[int] = 1
#: [Methods]
#:   None
b = Tally("b")
print(Tally.total)
#: 2
# a.total = 99  # ty: cannot assign ClassVar "total" via instance
