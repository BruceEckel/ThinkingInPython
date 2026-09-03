# missing_super.py
from simple_class import Simple

class Broken(Simple):
    def __init__(self, text):
        pass  # Forgot super().__init__(text)

try:
    Broken("ignored").show()
except AttributeError as e:
    print(e)
#: 'Broken' object has no attribute 's'
