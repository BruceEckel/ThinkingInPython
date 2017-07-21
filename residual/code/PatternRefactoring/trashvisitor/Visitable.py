# PatternRefactoring/trashvisitor/Visitable.py
# An class to add visitor functionality
# to the Trash hierarchy without
# modifying the base class.

class Visitable:
    # The method:
    def accept(self, Visitor v)