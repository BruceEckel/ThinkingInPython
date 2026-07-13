# test_register.py
from register import Espresso, Latte, register, registry

def test_register_returns_same_class() -> None:
    assert register(Espresso) is Espresso

def test_registry_looks_up_by_name() -> None:
    assert registry["Espresso"] is Espresso
    assert registry["Latte"] is Latte
