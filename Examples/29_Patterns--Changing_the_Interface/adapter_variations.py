# adapter_variations.py
# Two more places to put the adaptation.
from typing import Any, override
from adapter import (ProxyAdapter, WhatIHave, WhatIUse,
                     WhatIWant)

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    @override
    # def op(self, what_i_have: WhatIHave) -> None:
    def op(self, what_i_have: Any) -> None:
        ProxyAdapter(what_i_have).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        self.g()
        self.h()

WhatIUse2().op(WhatIHave())  # Approach 2: adapting op()
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse().op(WhatIHave2())  # Approach 3: adapter built in
#: WhatIHave.g()
#: WhatIHave.h()
