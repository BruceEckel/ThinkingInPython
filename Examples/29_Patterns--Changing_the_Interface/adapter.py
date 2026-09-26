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
    what_i_have: WhatIHave

    @override
    def f(self) -> None:
        # Implement behavior using WhatIHave:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant, /) -> None:
        what_i_want.f()

if __name__ == "__main__":
    adapt = ProxyAdapter(WhatIHave())
    WhatIUse().op(adapt)
#: WhatIHave.g()
#: WhatIHave.h()
