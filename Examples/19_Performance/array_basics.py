# array_basics.py
from array import array

a = array("d", [1.0, 2.0, 3.0])  # "d" = C double
a.append(4.0)
print(a)
#: array('d', [1.0, 2.0, 3.0, 4.0])
print(a[1], a.typecode, a.itemsize)
#: 2.0 d 8
try:
    # The value must match the type code:
    a.append("x")  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
