# compose.py

class Compose:
    from utility import f

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Compose({self.name!r})"

Compose("example").f()
## utility.f() called on Compose('example')
