# adapter_variations.py
from typing import override
from adapter import (ProxyAdapter, WhatIHave, WhatIUse,
                     WhatIWant)

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    @override
    # With WhatIHave alone, ty rejects the override:
    # def op(self, item: WhatIHave) -> None:
    def op(self, item: WhatIWant | WhatIHave) -> None:
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                ProxyAdapter(item).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        self.g()
        self.h()

WhatIUse2().op(WhatIHave())  # Approach 2
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(ProxyAdapter(WhatIHave()))
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse().op(WhatIHave2())  # Approach 3
#: WhatIHave.g()
#: WhatIHave.h()
