# pool_demo.py
from contextlib import suppress
from object_pool import Connection, Pool

pool = Pool(Connection(1), Connection(2))
with pool.lease() as conn:
    print(conn.query("SELECT name FROM users"))
    print("available during lease:", pool.available())
#: connection 1: SELECT name FROM users
#: available during lease: 1
print("available after lease:", pool.available())
#: available after lease: 2
with suppress(RuntimeError), pool.lease():
    raise RuntimeError("crash during query")
print("available after crash:", pool.available())
#: available after crash: 2
