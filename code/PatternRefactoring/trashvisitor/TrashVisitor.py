# PatternRefactoring/trashvisitor/TrashVisitor.py
# The "visitor" pattern with VisitableDecorators.

# Specific group of algorithms packaged
# in each implementation of Visitor:
class PriceVisitor(Visitor):
    alSum = 0.0 # Aluminum
    pSum = 0.0  # Paper
    gSum = 0.0  # Glass
    cSum = 0.0  # Cardboard
    def visit(self, al):
        v = al.getWeight() * al.getValue()
        print("value of Aluminum= " + v)
        alSum += v

    def visit(self, p):
        v = p.getWeight() * p.getValue()
        print("value of Paper= " + v)
        pSum += v

    def visit(self, g):
        v = g.getWeight() * g.getValue()
        print("value of Glass= " + v)
        gSum += v

    def visit(self, c):
        v = c.getWeight() * c.getValue()
        print("value of Cardboard = " + v)
        cSum += v

    def total(self):
        print (
          "Total Aluminum: $" + alSum +
          "\n Total Paper: $" + pSum +
          "\nTotal Glass: $" + gSum +
          "\nTotal Cardboard: $" + cSum +
          "\nTotal: $" +
            (alSum + pSum + gSum + cSum))

class WeightVisitor(Visitor):
    alSum = 0.0  # Aluminum
    pSum = 0.0  # Paper
    gSum = 0.0  # Glass
    cSum = 0.0  # Cardboard
    def visit(self, Aluminum al):
        alSum += al.getWeight()
        print ("weight of Aluminum = "
            + al.getWeight())

    def visit(self, Paper p):
        pSum += p.getWeight()
        print ("weight of Paper = "
            + p.getWeight())

    def visit(self, Glass g):
        gSum += g.getWeight()
        print ("weight of Glass = "
            + g.getWeight())

    def visit(self, Cardboard c):
        cSum += c.getWeight()
        print ("weight of Cardboard = "
            + c.getWeight())

    def total(self):
        print (
          "Total weight Aluminum: "  + alSum +
          "\nTotal weight Paper: " + pSum +
          "\nTotal weight Glass: " + gSum +
          "\nTotal weight Cardboard: " + cSum +
          "\nTotal weight: " +
            (alSum + pSum + gSum + cSum))

class TrashVisitor(UnitTest):
    Bin = ArrayList()
    PriceVisitor pv = PriceVisitor()
    WeightVisitor wv = WeightVisitor()
    def __init__(self):
        ParseTrash.fillBin("../trash/Trash.dat",
          FillableVisitor(
            FillableCollection(bin)))

    def test(self):
        Iterator it = bin.iterator()
        while(it.hasNext()):
            Visitable v = (Visitable)it.next()
            v.accept(pv)
            v.accept(wv)

        pv.total()
        wv.total()

    def main(self, String args[]):
        TrashVisitor().test()