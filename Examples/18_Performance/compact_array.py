# compact_array.py
import sys
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

nums = [float(i) for i in range(10_000)]
packed = array("d", nums)
list_bytes = sys.getsizeof(nums) + sum(
    sys.getsizeof(x) for x in nums
)
array_bytes = sys.getsizeof(packed)
print(f"array at least 3x smaller: "
      f"{array_bytes * 3 < list_bytes}")
#: array at least 3x smaller: True
