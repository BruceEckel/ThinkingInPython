# display_messenger.py
from dataclasses import dataclass
from display import display_object

@dataclass
class Messenger:
    name: str
    number: int
    depth: float = 0.0

display_object(Messenger("foo", 12, 3.14))
## === Messenger ===
## [Attributes]
##   • depth: float = 3.14
##   • name: str = 'foo'
##   • number: int = 12
## [Methods]
##   None
