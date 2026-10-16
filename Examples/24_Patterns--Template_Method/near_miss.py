# near_miss.py
from difflib import get_close_matches
from typing import override
from exceptions import expected
from framework import ApplicationFramework

class CheckedFramework(ApplicationFramework):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        inherited = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            replaced = getattr(super(cls, cls), name, None)
            if getattr(replaced, "__final__", False):
                raise TypeError(
                    f"{cls.__name__}.{name} "
                    "overrides a @final method"
                )
            if name in inherited:
                continue
            if near := get_close_matches(name, inherited):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(CheckedFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Typo(CheckedFramework):
        def customise1(self) -> None:
            print("never runs")
#: [TypeError] Typo.customise1: did you mean customize1?

with expected(TypeError):
    class Hijack(CheckedFramework):
        def run(self) -> None:  # type: ignore
            print("never runs")
#: [TypeError] Hijack.run overrides a @final method

with expected(TypeError):
    class Weird(CheckedFramework):
        def customer(self) -> None: ...
#: [TypeError] Weird.customer: did you mean customize2?
