# squasher_generator.py
from collections.abc import Iterator

def squash(chars: Iterator[str]) -> Iterator[str]:
    for char in chars:
        if char != "*":
            yield char
            continue
        # We have a *, what's the next one?
        match next(chars, ""):
            case "*":  # A second *
                yield "^"
            case "":  # No more input
                yield "*"
            case following_char:  # Something else
                yield "*"  # [1]
                yield following_char  # [2]

print(list(squash(iter("a**b*c***"))))
#: ['a', '^', 'b', '*', 'c', '^', '*']
