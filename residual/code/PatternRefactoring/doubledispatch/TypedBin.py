# PatternRefactoring/doubledispatch/TypedBin.py
# A container for the second dispatch.

class TypedBin:
    c = ArrayList()
    def addIt(self, Trash t):
        c.add(t)
        return True

    def iterator(self):
        return c.iterator()

    def add(self, DDAluminum a):
        return False

    def add(self, DDPaper a):
        return False

    def add(self, DDGlass a):
        return False

    def add(self, DDCardboard a):
        return False