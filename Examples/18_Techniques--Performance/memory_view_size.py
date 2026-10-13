# memory_view_size.py
import sys
from benchmark import report

big = bytearray(1_000_000)
copied = big[:500_000]
viewed = memoryview(big)[:500_000]
copy_bytes = sys.getsizeof(copied)
view_bytes = sys.getsizeof(viewed)
report(copy_bytes=copy_bytes, view_bytes=view_bytes)
print(f"view under 1% of copy: "
      f"{view_bytes * 100 < copy_bytes}")
#: view under 1% of copy: True
print(viewed.nbytes)
#: 500000
