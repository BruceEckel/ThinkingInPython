# DataClassesAsTypes/stars_unchecked.py
# A bare int for a 1-10 rating must be re-checked everywhere it is used.
from validation import check


def f1(stars: int) -> int:
    check(1 <= stars <= 10, f"f1({stars})")  # Check the argument here...
    return stars + 5


def f2(stars: int) -> int:
    check(1 <= stars <= 10, f"f2({stars})")  # ...and again here.
    return stars * 5


if __name__ == "__main__":
    rating = 6
    print(rating)
    print(f1(rating))
    print(f2(rating))
