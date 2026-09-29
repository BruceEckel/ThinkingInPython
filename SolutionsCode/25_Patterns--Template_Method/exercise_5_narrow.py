# exercise_5_narrow.py
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
        declared = {
            name
            for name in vars(ApplicationFramework)
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
            if name in declared:
                continue
            if near := get_close_matches(name, declared):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

class Audited(MyApp):
    def reports(self) -> None: ...

print(Audited.reports.__qualname__)
#: Audited.reports

with expected(TypeError):
    class Typo(MyApp):
        def customise2(self) -> None: ...
#: [TypeError] Typo.customise2: did you mean customize2?
