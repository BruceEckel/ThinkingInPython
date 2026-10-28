# chain.py
from algorithms import Fn, Hint, Root, RootFinder

def first_root(f: Fn, a: Hint, b: Hint,
               chain: list[RootFinder]) -> Root | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None
