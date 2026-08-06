# finalizer.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.closer = finalize(self, print, name, "closed")

    def close(self) -> None:
        self.closer()

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.close()
#: A closed
a.close()
print(a.closer.alive, b.closer.alive)
#: False True
del b
#: B closed
print("End of program")
#: End of program
