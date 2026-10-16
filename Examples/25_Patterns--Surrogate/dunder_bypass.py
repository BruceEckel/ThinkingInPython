# dunder_bypass.py
from exceptions import expect
from proxy_getattr import Proxy

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return " ".join(self.items)

w = Words()
p = Proxy(w)
print(p.__len__())  # The explicit call delegates
#: 2
# Special-method lookup skips the instance:
expect(TypeError, len, p)  # type: ignore
#: [TypeError] object of type 'Proxy' has no len()
print(w, "|", str(p).split(" at ")[0])
#: spam eggs | <proxy_getattr.Proxy object
