# functools_partialmethod.py
from dataclasses import dataclass
from functools import partialmethod

@dataclass
class Text:
    value: str

    def pad(self, width: int, fill: str = " ") -> str:
        return self.value.rjust(width, fill)

    zero_pad = partialmethod(pad, fill="0")

print(Text("7").zero_pad(3))
#: 007
