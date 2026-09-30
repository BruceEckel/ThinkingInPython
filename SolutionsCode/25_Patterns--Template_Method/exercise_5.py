# exercise_5.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

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

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Audited(MyApp):
        def reports(self) -> None: ...
#: [TypeError] Audited.reports: did you mean report?
