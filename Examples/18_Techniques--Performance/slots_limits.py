# slots_limits.py
import weakref
from dataclasses import dataclass
from functools import cached_property

@dataclass(slots=True)
class Node:
    value: int

    @cached_property
    def doubled(self) -> int:
        return self.value * 2

node = Node(3)
try:
    print(node.doubled)
except TypeError as e:
    # cached_property needs a __dict__ to write into:
    print(str(e).partition(" to cache")[0])
#: No '__dict__' attribute on 'Node' instance

@dataclass(slots=True)
class Slotted:
    x: int

try:
    weakref.ref(Slotted(1))
except TypeError as e:
    # No __weakref__ slot unless you declare one:
    print(str(e))
#: cannot create weak reference to 'Slotted' object

@dataclass(slots=True)
class OtherSlotted:
    y: int

try:
    class Both(  # type: ignore
        Slotted, OtherSlotted
    ):
        pass
except TypeError as e:
    # Two nonempty slot layouts cannot combine:
    print(str(e))
#: multiple bases have instance lay-out conflict
