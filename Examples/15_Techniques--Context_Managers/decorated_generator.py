# decorated_generator.py
from collections.abc import Iterator
from context_decorator import banner

@banner("rows")
def rows() -> Iterator[int]:
    for n in range(3):
        print(f"yield {n}")
        yield n

gen = rows()
print("created")
#: created
for row in gen:
    print(f"got {row}")
#: === rows ===
#: yield 0
#: got 0
#: yield 1
#: got 1
#: yield 2
#: got 2
#: === rows ends ===
print("done")
#: done
