# adapter.py
# Variations on the Adapter pattern.
from typing import Any, override

class WhatIHave:
    def g(self) -> None: pass
    def h(self) -> None: pass

class WhatIWant:
    def f(self) -> None: pass

class ProxyAdapter(WhatIWant):
    def __init__(self, what_i_have: Any) -> None:
        self.what_i_have = what_i_have

    @override
    def f(self) -> None:
        # Implement behavior using
        # methods in WhatIHave:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: Any, /) -> None:
        what_i_want.f()

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    @override
    def op(self, what_i_have: Any) -> None:
        ProxyAdapter(what_i_have).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        self.g()
        self.h()

# Approach 4: use an inner class:
class WhatIHave3(WhatIHave):
    class InnerAdapter(WhatIWant):
        def __init__(self, outer: Any) -> None:
            self.outer = outer
        @override
        def f(self) -> None:
            self.outer.g()
            self.outer.h()

    def what_i_want(self) -> WhatIWant:
        return WhatIHave3.InnerAdapter(self)

what_i_use = WhatIUse()
what_i_have = WhatIHave()
adapt = ProxyAdapter(what_i_have)
what_i_use2 = WhatIUse2()
what_i_have2 = WhatIHave2()
what_i_have3 = WhatIHave3()
what_i_use.op(adapt)
# Approach 2:
what_i_use2.op(what_i_have)
# Approach 3:
what_i_use.op(what_i_have2)
# Approach 4:
what_i_use.op(what_i_have3.what_i_want())
