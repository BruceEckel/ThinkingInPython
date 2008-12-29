# PatternRefactoring/doubledispatch/DoubleDispatch.py
# Using multiple dispatching to handle more
# than one unknown type during a method call.

class AluminumBin(TypedBin):
    def add(self, DDAluminum a):
        return addIt(a)

class PaperBin(TypedBin):
    def add(self, DDPaper a):
        return addIt(a)

class GlassBin(TypedBin):
    def add(self, DDGlass a):
        return addIt(a)

class CardboardBin(TypedBin):
    def add(self, DDCardboard a):
        return addIt(a)

class TrashBinSet:
    binSet = [
      AluminumBin(),
      PaperBin(),
      GlassBin(),
      CardboardBin()
    ]

    def sortIntoBins(self, bin):
        Iterator e = bin.iterator()
        while(e.hasNext()):
            TypedBinMember t =
                (TypedBinMember)e.next()
            if(!t.addToBin(binSet))
                System.err.println("Couldn't add " + t)

    def binSet(): return binSet

class DoubleDispatch(UnitTest):
    Bin = ArrayList()
    TrashBinSet bins = TrashBinSet()
    def __init__(self):
        # ParseTrash still works, without changes:
        ParseTrash.fillBin("DDTrash.dat", bin)

    def test(self):
        # Sort from the master bin into
        # the individually-typed bins:
        bins.sortIntoBins(bin)
        TypedBin[] tb = bins.binSet()
        # Perform sumValue for each bin...
        for(int i = 0 i < tb.length i++)
            Trash.sumValue(tb[i].c.iterator())
        # ... and for the master bin
        Trash.sumValue(bin.iterator())

    def main(self, String args[]):
        DoubleDispatch().test()