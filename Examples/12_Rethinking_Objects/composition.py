# composition.py
# Build new types by composing data, not by inheriting implementation.
# replace() copies with changes, and frozen instances compare and hash.
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Name:
    first: str
    last: str


@dataclass(frozen=True)
class Address:
    city: str
    postal: str


@dataclass(frozen=True)
class Contact:  # A Contact has a Name and an Address.
    name: Name
    address: Address


if __name__ == "__main__":
    c = Contact(Name("Bruce", "Eckel"), Address("Crested Butte", "81224"))
    print(c)

    moved = replace(c, address=replace(c.address, city="Carbondale"))
    print(moved)

    print(c == Contact(Name("Bruce", "Eckel"), Address("Crested Butte", "81224")))
    print({c: "value"}[c])  # Hashable, so it works as a dict key.
