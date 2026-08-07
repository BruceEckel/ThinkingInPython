# compose.py

class Compose:
    from utility import f

    def __init__(self, name):
        self.name = name

class Other:
    from utility import f

    def __init__(self, name):
        self.name = name

Compose("example").f()
#: utility.f() called on example
Other("second").f()
#: utility.f() called on second
