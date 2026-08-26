# exercise_4.py
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Exploder(ApplicationFramework):
    @override
    def customize1(self) -> None:
        raise RuntimeError("step 1 refuses")

class HalfDone(ApplicationFramework):
    def __init__(self) -> None:
        self.pending: list[str] = []

    @override
    def customize1(self) -> None:
        self.pending.append("work")
    # The `...` default on customize2() drains nothing

try:
    Exploder().run()
except RuntimeError as e:
    print(e)
#: step 1 refuses

app = HalfDone()
app.run()
print(app.pending)
#: ['work', 'work']
