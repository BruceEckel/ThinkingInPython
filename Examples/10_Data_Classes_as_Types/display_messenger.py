# display_messenger.py
from display import display_object
from messenger import Messenger

display_object(Messenger("foo", 12, 3.14))
#: Messenger(name='foo', number=12, depth=3.14)
#: foo 12 3.14
#: True
#: False
#: Messenger(name='foo', number=12, depth=3.14)
#: Messenger(name='foo', number=12, depth=9.9)
#: Messenger(name='bar', number=12, depth=3.14)
#: === Messenger ===
#: [Attributes]
#:   • depth: float = 3.14
#:   • name: str = 'foo'
#:   • number: int = 12
#: [Methods]
#:   None
