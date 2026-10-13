# frozen_containers.py

primes = frozenset({2, 3, 5, 7})
print(5 in primes)
#: True
groups = {frozenset({1, 2}), frozenset({3, 4})}
print(frozenset({1, 2}) in groups)
#: True
try:
    primes.add(11)  # type: ignore
except AttributeError as e:
    print(e)
#: 'frozenset' object has no attribute 'add'
