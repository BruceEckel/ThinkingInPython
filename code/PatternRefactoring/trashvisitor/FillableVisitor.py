# PatternRefactoring/trashvisitor/FillableVisitor.py
# Adapter Decorator that adds the visitable
# decorator as the Trash objects are
# being created.

class FillableVisitor(Fillable):
    def __init__(self, ff): self.f = ff
    def addTrash(self, t):
        self.f.addTrash(VisitableDecorator(t))