# adapter_variations.py
# Three more places to put the adaptation.
from typing import Any, override
from adapter import ProxyAdapter, WhatIHave, WhatIUse, WhatIWant

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
        def __init__(self, outer: WhatIHave3) -> None:
            self.outer = outer
        @override
        def f(self) -> None:
            self.outer.g()
            self.outer.h()

    def what_i_want(self) -> WhatIWant:
        return WhatIHave3.InnerAdapter(self)

what_i_use = WhatIUse()
WhatIUse2().op(WhatIHave())  # Approach 2: adapting op()
#: WhatIHave.g()
#: WhatIHave.h()
what_i_use.op(WhatIHave2())  # Approach 3: adapter built in
#: WhatIHave.g()
#: WhatIHave.h()
what_i_use.op(WhatIHave3().what_i_want())  # Approach 4
#: WhatIHave.g()
#: WhatIHave.h()
