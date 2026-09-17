# test_adapter.py
from getattr_adapter import Adapter, WhatIHave

def test_new_interface_combines_methods() -> None:
    assert Adapter(WhatIHave()).f(2) == "ffgghh"

def test_getattr_forwards_existing_methods_unchanged(
) -> None:
    a = Adapter(WhatIHave())
    assert a.g(2) == "gg"
    assert a.h(3) == "hhh"

def test_forwarding_targets_the_wrapped_object() -> None:
    have = WhatIHave()
    a = Adapter(have)
    # __getattr__ delegates to adaptee
    assert a.g.__self__ is have
