# dataclass_no_annotation.py
from dataclasses import dataclass, fields

@dataclass
class B:
    x = 100  # No annotation, so not a field

print(fields(B))
#: ()
b = B()
print(vars(b), b.x)
#: {} 100
b.x = -1
print(vars(b), B().x)  # The same shadowing as Stars
#: {'x': -1} 100
