# patternRefactoring/recyclea/RecycleA.py
# Recycling with RTTI.

class Trash:
    def __init__(self, wt):
        self.weight = wt
    abstract def getValue()
    def getWeight(): return weight
    # Sums the value of Trash in a bin:
    def sumValue(Iterator it):
        val = 0.0f
        while(it.hasNext()):
            # One kind of RTTI:
            # A dynamically-checked cast
            Trash t = (Trash)it.next()
            # Polymorphism in action:
            val += t.getWeight() * t.getValue()
            print (
              "weight of " +
              # Using RTTI to get type
              # information about the class:
              t.getClass().getName() +
              " = " + t.getWeight())

        print("Total value = " + val)

class Aluminum(Trash):
    val  = 1.67f
    def __init__(self, wt):
        Trash.__init__(wt)
    def getValue(): return self.val
    setValue(newval):
        val = newval

class Paper(Trash):
    val = 0.10f
    def __init__(self, wt):
        Trash.__init__(wt)
    def getValue(): return self.val
    def setValue(self, newval):
        val = newval

class Glass(Trash):
    val = 0.23f
    def __init__(self, wt):
        Trash.__init__(wt)
    def getValue(self):
        return self.val
    def setValue(self, newval):
        val = newval

class RecycleA(UnitTest):
    bin = ArrayList()
    glassBin = ArrayList()
    paperBin = ArrayList()
    alBin = ArrayList()
    def __init__(self):
        # Fill up the Trash bin:
        for(int i = 0 i < 30 i++)
            switch((int)(Math.random() * 3)):
                case 0:
                    bin.add(new
                      Aluminum(Math.random() * 100))
                    break
                case 1:
                    bin.add(new
                      Paper(Math.random() * 100))
                    break
                case 2:
                    bin.add(new
                      Glass(Math.random() * 100))

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
        RecycleA().test()