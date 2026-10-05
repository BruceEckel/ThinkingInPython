# test_adapter.py
import copy
import pickle
from getattr_adapter import Adapter, WhatIHave

def test_f_puts_its_output_before_g_and_h() -> None:
    assert Adapter(WhatIHave()).f(2) == "ffgghh"

def test_getattr_forwards_existing_methods_unchanged(
) -> None:
    a = Adapter(WhatIHave())
    assert a.g(2) == "gg"
    assert a.h(3) == "hhh"

def test_forwarded_method_is_bound_to_the_adaptee() -> None:
    have = WhatIHave()
    a = Adapter(have)
    assert not hasattr(Adapter, "g")
    assert a.g.__self__ is have

def test_copy_and_pickle_rebuild_the_adapter() -> None:
    a = Adapter(WhatIHave())
    assert copy.copy(a).f(1) == "fgh"
    restored = pickle.loads(pickle.dumps(a))
    assert restored.g(2) == "gg"
