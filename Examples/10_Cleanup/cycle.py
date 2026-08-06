# cycle.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def self_link() -> None:
    node = Node("a")
    node.peer = node

gc.disable()
self_link()
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
gc.enable()
print("after collect")
#: after collect
