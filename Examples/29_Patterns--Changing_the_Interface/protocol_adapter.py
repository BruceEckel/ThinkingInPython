# protocol_adapter.py
from typing import Protocol
from adapter import WhatIHave
from record import record

class WhatIWant(Protocol):
    def f(self) -> None: ...

@record
class ObjectAdapter:
    what_i_have: WhatIHave

    def f(self) -> None:
        self.what_i_have.g()
        self.what_i_have.h()

def use(what_i_want: WhatIWant, /) -> None:
    what_i_want.f()

use(ObjectAdapter(WhatIHave()))
#: WhatIHave.g()
#: WhatIHave.h()
