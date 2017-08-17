# InitializationAndCleanup/static_idiom.py
class Foo:
    something = None # Static: visible to all classes
def f(self, x):
    if not self.something:
        self.something = [] # New local version for this object
    self.something.append(x)
