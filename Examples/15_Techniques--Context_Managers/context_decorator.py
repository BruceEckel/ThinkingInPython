# context_decorator.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Generator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("quarterly")
def quarterly() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    quarterly()
    with banner("meeting"):
        print("agenda")
#: === quarterly ===
#: quarterly numbers
#: === quarterly ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
