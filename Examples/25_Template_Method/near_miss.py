# near_miss.py
from difflib import get_close_matches
from typing import final, override

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
        hooks = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name in hooks or name.startswith("__"):
                continue
            if near := get_close_matches(name, hooks):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

try:
    class Typo(ApplicationFramework):
        def customise1(self) -> None:
            print("never runs")
except TypeError as e:
    print(e)
#: Typo.customise1: did you mean customize1?
