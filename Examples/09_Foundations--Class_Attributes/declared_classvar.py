# declared_classvar.py
from typing import ClassVar
from exceptions import expected

class Registry:
    count: ClassVar[int]  # Declared, no value

with expected(AttributeError):
    print(Registry.count)
#: [AttributeError] type object 'Registry' has no attribute
#: 'count'

Registry.count = 0  # The assignment creates it
print(Registry.count)
#: 0
print(Registry().count)  # Found by fallback
#: 0
