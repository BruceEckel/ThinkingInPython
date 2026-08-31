# adapter.py
# The object adapter.
from typing import override

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    def f(self) -> None: ...

class ProxyAdapter(WhatIWant):
    def __init__(self, what_i_have: WhatIHave) -> None:
        self.what_i_have = what_i_have

    @override
    def f(self) -> None:
        # Implement behavior using
        # methods in WhatIHave:
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
