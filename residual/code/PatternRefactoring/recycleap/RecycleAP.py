# PatternRefactoring/recycleap/RecycleAP.py
# Recycling with RTTI and Prototypes.

class RecycleAP(UnitTest):
    Collection
        bin = ArrayList(),
        glassBin = ArrayList(),
        paperBin = ArrayList(),
        alBin = ArrayList()
    def __init__(self):
        # Fill up the Trash bin:
        ParseTrash.fillBin(
          "../trash/Trash.dat", bin)

    def test(self):
        Iterator sorter = bin.iterator()
        # Sort the Trash:
        while(sorter.hasNext()):
            Object t = sorter.next()
            # RTTI to show class membership:
            if(t instanceof Aluminum)
                alBin.add(t)
            if(t instanceof Paper)
                paperBin.add(t)
            if(t instanceof Glass)
                glassBin.add(t)

        Trash.sumValue(alBin.iterator())
        Trash.sumValue(paperBin.iterator())
        Trash.sumValue(glassBin.iterator())
        Trash.sumValue(bin.iterator())

    def main(self, String args[]):
        RecycleAP().test()