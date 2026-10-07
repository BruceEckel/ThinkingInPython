# faithless_step.py
from typing import override
from framework import ApplicationFramework

class OnlyOnce(ApplicationFramework):
    def __init__(self) -> None:
        self._ran = False

    @override
    def customize1(self) -> None:
        if not self._ran:  # The second pass does nothing
            self._ran = True
            print("Nudge, nudge, wink, wink!")

OnlyOnce().run()
#: Nudge, nudge, wink, wink!
