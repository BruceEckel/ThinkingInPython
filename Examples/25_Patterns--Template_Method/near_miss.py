# near_miss.py
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
        hooks = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            if name == "run":
                raise TypeError(
                    f"{cls.__name__}.run "
                    "overrides the anchor"
                )
            if name in hooks:
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

with expected(TypeError):
    class Typo(ApplicationFramework):
        def customise1(self) -> None:
            print("never runs")
#: [TypeError] Typo.customise1: did you mean customize1?

with expected(TypeError):
    class Hijack(ApplicationFramework):
        def run(self) -> None:  # type: ignore
            print("never runs")
#: [TypeError] Hijack.run overrides the anchor

with expected(TypeError):
    class Weird(ApplicationFramework):
        def customized_report(self) -> None: ...
#: [TypeError] Weird.customized_report: did you mean
#: customize2?
