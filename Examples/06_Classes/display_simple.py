# display_simple.py
from display import display_object
from simple_class import Simple

x = Simple("Constructor argument")
#: Inside the Simple constructor
display_object(x)
#: === Simple ===
#: [Attributes]
#:   • s = 'Constructor argument'
#: [Methods]
#:   • show(self, msg='')
#:   • show_twice(self)
