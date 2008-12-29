# PatternRefactoring/recycleb/RecycleB.py
# Containers that grab objects of interest.

# A container that admits only the right type
# of Trash (established in the constructor):
class Tbin:
    def __init__(self, binType):
        self.list = ArrayList()
        self.type = binType
    def grab(self, t):
        # Comparing class types:
        if(t.getClass().equals(self.type)):
            self.list.add(t)
            return True # Object grabbed

        return False # Object not grabbed

    def iterator(self):
        return self.list.iterator()

class TbinList(ArrayList):
    def sort(self, Trash t):
        Iterator e = iterator() # Iterate over self
        while(e.hasNext())
            if(((Tbin)e.next()).grab(t)) return
        # Need a Tbin for this type:
        add(Tbin(t.getClass()))
        sort(t) # Recursive call

class RecycleB(UnitTest):
    Bin = ArrayList()
    TbinList trashBins = TbinList()
    def __init__(self):
        ParseTrash.fillBin("../trash/Trash.dat",bin)

    def test(self):
        Iterator it = bin.iterator()
        while(it.hasNext())
            trashBins.sort((Trash)it.next())
        Iterator e = trashBins.iterator()
        while(e.hasNext()):
            Tbin b = (Tbin)e.next()
            Trash.sumValue(b.iterator())

        Trash.sumValue(bin.iterator())

    def main(self, String args[]):
        RecycleB().test()