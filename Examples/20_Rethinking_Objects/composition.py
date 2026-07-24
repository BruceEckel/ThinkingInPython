# composition.py
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
    Name("Gerald", "Spigot-Farthingale"),
    Address("Sodding-on-the-Wold", "12345")
)
print(c.name)
#: Name(first='Gerald', last='Spigot-Farthingale')
print(c.address)
#: Address(city='Sodding-on-the-Wold', postal='12345')

# A copy with one nested field changed leaves c intact
moved = replace(c,
    address=replace(c.address, city="Fenwick-under-Custard"))
print(c.address.city, "->", moved.address.city)
#: Sodding-on-the-Wold -> Fenwick-under-Custard

twin = Contact(
    Name("Gerald", "Spigot-Farthingale"),
    Address("Sodding-on-the-Wold", "12345")
)
print(c == twin)  # Value equality, field by field
#: True
print({c: "value"}[c])  # Hashable, so it works as a dict key
#: value
