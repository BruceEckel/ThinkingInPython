# leaked_lease.py
from object_pool import Connection, Pool

pool = Pool(Connection(1))
with pool.lease() as first:
    stale = first  # Escapes the block

with pool.lease() as second:
    print(stale is second)
    print(stale.query("late"))
#: True
#: connection 1: late
