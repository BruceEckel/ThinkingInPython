# exercise_4.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"],
                     more=11, extra="stuff")
display_object(m)
#: === SimpleNamespace ===
#: [Attributes]
#:   • b = ['a', 'list']
#:   • extra = 'stuff'
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
