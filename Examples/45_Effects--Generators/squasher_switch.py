# squasher_switch.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass
class Squasher(Iterator[str]):
    chars: Iterator[str]
    _held: str = field(default="", init=False)

    @override
    def __next__(self) -> str:
        if self._held:  # [1]
            held, self._held = self._held, ""
            return held
        char = next(self.chars)
        if char != "*":
            return char
        # We have a *, what's the next one?
        match next(self.chars, ""):
            case "*":  # A second *
                return "^"
            case "":  # No more input
                return "*"
            case following_char:  # Something else
                # Stash it for the subsequent next() call:
                self._held = following_char  # [2]
                return "*"

print(list(Squasher(iter("a**b*c***"))))
#: ['a', '^', 'b', '*', 'c', '^', '*']
