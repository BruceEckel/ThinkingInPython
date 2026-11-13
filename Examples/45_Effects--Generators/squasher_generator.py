# squasher_generator.py
from collections.abc import Iterator

def squash(chars: Iterator[str]) -> Iterator[str]:
    for char in chars:
        if char != "*":
            yield char
            continue
        match next(chars, ""):
            case "*":
                yield "^"
            case "":  # No more input
                yield "*"
            case following:
                yield "*"  # [1]
                yield following  # [2]

print(list(squash(iter("a**b*c***"))))
#: ['a', '^', 'b', '*', 'c', '^', '*']
