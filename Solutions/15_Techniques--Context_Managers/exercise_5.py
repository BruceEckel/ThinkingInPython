# exercise_5.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Generator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("outer")
@banner("inner")
def report() -> None:
    print("quarterly numbers")

report()
#: === outer ===
#: === inner ===
#: quarterly numbers
#: === inner ends ===
#: === outer ends ===
