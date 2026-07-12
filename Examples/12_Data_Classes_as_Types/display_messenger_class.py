# display_messenger_class.py
from display import display_object
from messenger import Messenger

display_object(Messenger, dunder=["__init__", "__repr__", "__eq__"])
#: === Messenger ===
#: [Attributes]
#:   • depth: float = 0.0
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, name: str, number: int, depth: float = 0.0)...
#:   • __repr__(self)
