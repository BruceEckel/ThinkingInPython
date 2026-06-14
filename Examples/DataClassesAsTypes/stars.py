# DataClassesAsTypes/stars.py
# A type is a set of values. Validate once, at construction, in a frozen data
# class. Every Stars that exists is then guaranteed to be a legal value.
from dataclasses import dataclass
from validation import check


@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")


def f1(s: Stars) -> Stars:
    return Stars(s.number + 5)


def f2(s: Stars) -> Stars:
    return Stars(s.number * 5)


if __name__ == "__main__":
    rating = Stars(4)
    print(rating)
    print(f1(Stars(2)))
    print(f2(Stars(2)))
