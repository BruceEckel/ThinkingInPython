# PatternRefactoring/trash/Aluminum.py
# The Aluminum class with prototyping.

class Aluminum(Trash):
    val = 1.67f
    def __init__(self, wt): Trash.__init__(wt)
    def getValue(self): return val
    def setValue(self, newVal):
        self.val = newVal::


# PatternRefactoring/trash/Paper.py
# The Paper class with prototyping.

class Paper(Trash):
    val = 0.10f
    def __init__(self, wt): Trash.__init__(wt)
    def getValue(self): return self.val
    def setValue(self, newVal):
        self.val = newVal::


# PatternRefactoring/trash/Glass.py
# The Glass class with prototyping.

class Glass(Trash):
    val = 0.23f
    def __init__(self, wt): Trash.__init__(wt)
    def getValue(self): return self.val
    def setValue(self, newVal):
        self.val = newVal