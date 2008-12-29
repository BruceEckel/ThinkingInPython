# PatternRefactoring/trash/FillableCollection.py
# Adapter that makes a Collection Fillable.

class FillableCollection(Fillable):
    def __init__(self, cc):
        self.c = cc

    def addTrash(self, t):
        self.c.add(t)