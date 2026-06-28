# immutability.py
from types import MappingProxyType

# A tuple is an immutable list, and a frozenset is an immutable set:
nums = (1, 2, 3)
primes = frozenset({2, 3, 5, 7})
print(5 in primes)
#: True

# Immutable containers are hashable, so they can be set members
# or dictionary keys. A plain list or set cannot:
groups = {frozenset({1, 2}), frozenset({3, 4})}
print(frozenset({1, 2}) in groups)
#: True

# A dict has no frozen form, but MappingProxyType wraps one
# in a read-only view:
settings = {"debug": False, "level": 3}
config = MappingProxyType(settings)
print(config["level"])
#: 3

# Mutating any of them is an error:
try:
    primes.add(11)  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
try:
    config["level"] = 9  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
