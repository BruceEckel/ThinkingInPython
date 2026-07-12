# display_namespace.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
display_object(m)
#: [Attributes]
#:   • b = ['a', 'list']
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
