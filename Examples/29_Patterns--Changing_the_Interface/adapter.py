# adapter.py
from typing import override
from record import record

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    __slots__ = ()
    def f(self) -> None: ...

@record
class ProxyAdapter(WhatIWant):
    adaptee: WhatIHave

    @override
    def f(self) -> None:
        # Implement behavior using WhatIHave:
        self.adaptee.g()
        self.adaptee.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant, /) -> None:
        what_i_want.f()

if __name__ == "__main__":
    adapter = ProxyAdapter(WhatIHave())
    WhatIUse().op(adapter)
#: WhatIHave.g()
#: WhatIHave.h()
