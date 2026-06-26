# demo_display_object.py
from dataclasses import dataclass
from display import display_object

@dataclass
class Fraggle:
    x: int = 11
    y: float = 1.14659
    z: str = "blivet"

    def f(self, )-> None: ...
    def g(self, x: int)-> float:
        return 0.001
    def h(self, s: str)-> str:
        return f"h({s})"

display_object(Fraggle)
## === type ===
## [Attributes]
##   • x: 11
##   • y: 1.14659
##   • z: 'blivet'
## [Methods]
##   • f(self) -> None
##   • g(self, x: int) -> float
##   • h(self, s: str) -> str
display_object(Fraggle(9, 2.3, 'zingo'))
## === Fraggle ===
## [Attributes]
##   • x: 9
##   • y: 2.3
##   • z: 'zingo'
## [Methods]
##   • f(self) -> None
##   • g(self, x: int) -> float
##   • h(self, s: str) -> str
