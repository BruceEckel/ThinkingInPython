# exercise_5.py
from typing import override
from exceptions import expect
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
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant) -> None:
        what_i_want.f()

class Renamed(WhatIUse):
    @override
    def op(  # type: ignore
        self, item: WhatIWant | WhatIHave
    ) -> None:
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                super().op(ProxyAdapter(item))

class WhatIUse2(WhatIUse):
    @override
    def op(
        self, what_i_want: WhatIWant | WhatIHave
    ) -> None:
        match what_i_want:
            case WhatIWant():
                super().op(what_i_want)
            case WhatIHave():
                super().op(ProxyAdapter(what_i_want))

def run(user: WhatIUse) -> None:
    user.op(what_i_want=ProxyAdapter(WhatIHave()))

run(WhatIUse())
#: WhatIHave.g()
#: WhatIHave.h()
expect(TypeError, run, Renamed())
#: [TypeError] Renamed.op() got an unexpected keyword
#: argument 'what_i_want'
run(WhatIUse2())
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(what_i_want=WhatIHave())
#: WhatIHave.g()
#: WhatIHave.h()
