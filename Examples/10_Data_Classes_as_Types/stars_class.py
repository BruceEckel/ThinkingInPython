# stars_class.py
# "A class is not a type." Encapsulation guards the value, but every
# method must re-check it, and the object stays mutable underneath.
from validation import check

class Stars:
    def __init__(self, number: int) -> None:
        self._number = number  # Private by convention.
        self._validate()

    def _validate(self) -> None:
        check(1 <= self._number <= 10, f"Stars({self._number})")

    @property
    def number(self) -> int:  # No setter: blocks outside mutation.
        return self._number

    def __str__(self) -> str:
        return f"Stars({self._number})"

    def f1(self, n: int) -> int:
        check(1 <= n <= 10, f"f1({n})")  # Precondition.
        self._number = n + 5
        self._validate()                 # Postcondition.
        return self._number

if __name__ == "__main__":
    rating = Stars(4)
    print(rating)
    print(rating.f1(3))
