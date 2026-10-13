# finalizer.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.finalizer = finalize(
            self, print, name, "closed"
        )

    def close(self) -> None:
        self.finalizer()

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.close()  # [1]
#: A closed
a.close()  # [2]
print(a.finalizer.alive, b.finalizer.alive)
#: False True
del b
#: B closed
print("End of program")
#: End of program
