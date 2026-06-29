# stars_unchecked.py
# An int as a 1-10 rating must be re-checked everywhere
from validation import check

def f1(stars: int) -> int:
    # Check the argument here...
    check(1 <= stars <= 10, f"f1({stars})")
    return stars + 5

def f2(stars: int) -> int:
    # ...and again in every other function
    check(1 <= stars <= 10, f"f2({stars})")
    return stars * 5

rating = 6
print(rating)
#: 6
print(f1(rating))
#: 11
print(f2(rating))
#: 30
