# template_method.py
from typing import final, override

class ApplicationFramework:
    def __init__(self) -> None:
        self.run()

    # The fixed algorithm. Subclasses supply the steps, not the flow:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

# Create an "application" by filling in the steps:
class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("Nudge, nudge, wink, wink!")

    @override
    def customize2(self) -> None:
        print("Say no more, say no more!")

MyApp()
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
