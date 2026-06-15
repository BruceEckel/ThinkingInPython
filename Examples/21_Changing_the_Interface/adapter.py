# adapter.py
# Variations on the Adapter pattern.

class WhatIHave:
    def g(self): pass
    def h(self): pass

class WhatIWant:
    def f(self): pass

class ProxyAdapter(WhatIWant):
    def __init__(self, what_i_have):
        self.what_i_have = what_i_have

    def f(self):
        # Implement behavior using
        # methods in WhatIHave:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want):
        what_i_want.f()

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    def op(self, what_i_have):
        ProxyAdapter(what_i_have).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    def f(self):
        self.g()
        self.h()

# Approach 4: use an inner class:
class WhatIHave3(WhatIHave):
    class InnerAdapter(WhatIWant):
        def __init__(self, outer):
            self.outer = outer
        def f(self):
            self.outer.g()
            self.outer.h()

    def what_i_want(self):
        return WhatIHave3.InnerAdapter(self)

what_i_use = WhatIUse()
what_i_have = WhatIHave()
adapt= ProxyAdapter(what_i_have)
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
