# newtype_boundary.py
from typing import NewType

UserId = NewType("UserId", int)

def lookup(uid: UserId) -> str:
    return f"user-{uid}"

if __name__ == "__main__":
    print(lookup(UserId(42)))
    # ty: expected "UserId", found "Literal[42]":
    print(lookup(42))  # type: ignore
#: user-42
#: user-42
