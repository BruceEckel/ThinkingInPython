# PatternRefactoring/trashvisitor/VAluminum.py
# Taking the previous approach of creating a
# specialized Aluminum for the visitor pattern.

class VAluminum(Aluminum, Visitable):
    def __init__(self, wt): Aluminum.__init__(wt)
    def accept(self, v):
        v.visit(self)