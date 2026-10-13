# chain.py
from algorithms import Fn, RootFinder

def first_root(f: Fn, a: float, b: float,
               chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None
