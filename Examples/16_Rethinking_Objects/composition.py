# composition.py
# Build new types by composing data, not by inheriting
# implementation. replace() copies with changes, and frozen
# instances compare and hash.
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
class Contact:  # A Contact has a Name and an Address
    name: Name
    address: Address

c = Contact(
    Name("Bruce", "Eckel"), Address("Crested Butte", "81224"))
print(c.name)
## Name(first='Bruce', last='Eckel')
print(c.address)
## Address(city='Crested Butte', postal='81224')

# A copy with one nested field changed leaves c intact
moved = replace(c, address=replace(c.address, city="Carbondale"))
print(c.address.city, "->", moved.address.city)
## Crested Butte -> Carbondale

twin = Contact(
    Name("Bruce", "Eckel"), Address("Crested Butte", "81224"))
print(c == twin)  # Value equality, field by field
## True
print({c: "value"}[c])  # Hashable, so it works as a dict key
## value
