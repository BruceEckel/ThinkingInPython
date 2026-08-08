# memory_view_size.py
import sys
from benchmark import report

big = bytearray(1_000_000)
copied = big[:500_000]
viewed = memoryview(big)[:500_000]
report(copy_bytes=sys.getsizeof(copied),
       view_bytes=sys.getsizeof(viewed))
print(f"view under 1% of copy: "
      f"{sys.getsizeof(viewed) * 100 < sys.getsizeof(copied)}")
#: view under 1% of copy: True
print(viewed.nbytes)
#: 500000
