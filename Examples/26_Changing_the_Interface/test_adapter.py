# test_adapter.py
from getattr_adapter import Adapter, WhatIHave

def test_new_interface_combines_methods() -> None:
    assert Adapter(WhatIHave()).f() == "gh"

def test_getattr_forwards_existing_methods_unchanged() -> None:
    a = Adapter(WhatIHave())
    assert a.g() == "g"
    assert a.h() == "h"

def test_forwarding_targets_the_wrapped_object() -> None:
    have = WhatIHave()
    a = Adapter(have)
    assert a.g.__self__ is have  # __getattr__ delegates to adaptee
