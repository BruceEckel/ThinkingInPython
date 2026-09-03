# faithless_step.py
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class OnlyOnce(ApplicationFramework):
    ran = False

    @override
    def customize1(self) -> None:
        if not self.ran:  # The second pass does nothing
            self.ran = True
            print("Nudge, nudge, wink, wink!")

OnlyOnce().run()
#: Nudge, nudge, wink, wink!
