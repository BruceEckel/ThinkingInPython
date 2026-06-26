# demo_display_object.py
from dataclasses import dataclass
from display import display_object

@dataclass
class Fraggle:
    x: int
    y: float = 1.14659
    z: str = "blivet"

    def f(self, )-> None: ...
    def g(self, x: int)-> float:
        return 0.001
    def h(self, s: str)-> str:
        return f"h({s})"

display_object(Fraggle)  # Display the class
## === Fraggle ===
## [Attributes]
##   • y: float = 1.14659
##   • z: str = 'blivet'
## [Methods]
##   • f(self) -> None
##   • g(self, x: int) -> float
##   • h(self, s: str) -> str

# Display a specific instance:
display_object(Fraggle(9, 2.3))
## === Fraggle ===
## [Attributes]
##   • x: int = 9
##   • y: float = 2.3
##   • z: str = 'blivet'
## [Methods]
##   • f(self) -> None
##   • g(self, x: int) -> float
##   • h(self, s: str) -> str
