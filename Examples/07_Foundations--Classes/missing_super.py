# missing_super.py
from exceptions import expect
from simple_class import Simple

class Broken(Simple):
    def __init__(self, text):
        pass  # Forgot super().__init__(text)

expect(AttributeError, Broken("ignored").show)
#: [AttributeError] 'Broken' object has no attribute 's'
