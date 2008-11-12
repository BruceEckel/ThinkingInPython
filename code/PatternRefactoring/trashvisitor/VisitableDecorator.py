# PatternRefactoring/trashvisitor/VisitableDecorator.py
# A decorator that adapts the generic Trash
# classes to the visitor pattern.

class VisitableDecorator(Trash, Visitable):
    def __init__(self, t):
        self.delegate = t
        try:
            self.dispatch = Visitor.class.getMethod (
              "visit", Class[]: t.getClass()
            )
        except ex:
            ex.printStackTrace()

    def getValue(self):
        return delegate.getValue()

    def getWeight(self):
        return delegate.getWeight()

    def accept(self, Visitor v):
        self.dispatch.invoke(v, delegate)