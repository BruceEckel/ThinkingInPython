# exercise_4.py
class Tally:
    total = 0  # Plain class attribute, no ClassVar
    label: str

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

a = Tally("a")
b = Tally("b")
print(Tally.total)
#: 2
a.total = 99  # This does NOT touch Tally.total
print(vars(a))
#: {'label': 'a', 'total': 99}
print(Tally.total)
#: 2
