# slots_limits.py
import weakref
from dataclasses import dataclass
from functools import cached_property
from exceptions import expect, expected

@dataclass(slots=True)
class Node:
    value: int

    @cached_property
    def doubled(self) -> int:
        return self.value * 2

node = Node(3)
with expected(TypeError):
    # cached_property needs a __dict__ to write into:
    print(node.doubled)
#: [TypeError] No '__dict__' attribute on 'Node' instance to
#: cache 'doubled' property.

@dataclass(slots=True)
class Slotted:
    x: int

# No __weakref__ slot unless you declare one:
expect(TypeError, weakref.ref, Slotted(1))
#: [TypeError] cannot create weak reference to 'Slotted'
#: object

@dataclass(slots=True)
class OtherSlotted:
    y: int

with expected(TypeError):
    # Two nonempty slot layouts cannot combine:
    class Both(  # type: ignore
        Slotted, OtherSlotted
    ):
        pass
#: [TypeError] multiple bases have instance lay-out conflict
