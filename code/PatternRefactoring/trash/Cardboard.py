# PatternRefactoring/trash/Cardboard.py
# The Cardboard class with prototyping.

class Cardboard(Trash):
    val = 0.23f
    def __init__(self, wt): Trash.__init__(wt)
    def getValue(self): return self.val
    def setValue(self, newVal):
        self.val = newVal