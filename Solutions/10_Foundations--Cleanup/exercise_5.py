# exercise_5.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.finalizer = finalize(self, self.close)

    def close(self) -> None:
        print(self.name, "closed")

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.finalizer()
#: A closed
a.finalizer()
print(a.finalizer.alive, b.finalizer.alive)
#: False True
del b
print("End of program")
#: End of program
