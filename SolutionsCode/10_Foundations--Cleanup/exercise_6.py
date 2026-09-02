# exercise_6.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def self_link() -> None:
    a, b = Node("a"), Node("b")
    a.peer = b
    b.peer = a

gc.disable()
self_link()
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
#: b finalized
gc.enable()
print("after collect")
#: after collect
