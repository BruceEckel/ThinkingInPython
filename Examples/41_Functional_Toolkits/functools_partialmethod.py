# functools_partialmethod.py
from functools import partialmethod

class Text:
    def __init__(self, value: str) -> None:
        self.value = value

    def pad(self, width: int, fill: str = " ") -> str:
        return self.value.rjust(width, fill)

    zero_pad = partialmethod(pad, fill="0")

print(Text("7").zero_pad(3))
#: 007
