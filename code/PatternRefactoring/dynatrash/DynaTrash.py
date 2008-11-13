# PatternRefactoring/dynatrash/DynaTrash.py
# Using a Map of Lists and RTTI
# to automatically sort trash into
# ArrayLists. This solution, despite the
# use of RTTI, is extensible.

# Generic TypeMap works in any situation:
class TypeMap:
    t = HashMap()
    def add(self, Object o):
        Class type = o.getClass()
        if(self.t.has_key(type))
            self.t.get(type).add(o)
        else:
            List v = ArrayList()
            v.add(o)
            t.put(type,v)

    def get(self, Class type):
        return (List)t.get(type)

    def keys(self):
        return t.keySet().iterator()

# Adapter class to allow callbacks
# from ParseTrash.fillBin():
class TypeMapAdapter(Fillable):
    TypeMap map
    def __init__(self, TypeMap tm): map = tm
    def addTrash(self, Trash t): map.add(t)

class DynaTrash(UnitTest):
    TypeMap bin = TypeMap()
    def __init__(self):
        ParseTrash.fillBin("../trash/Trash.dat",
          TypeMapAdapter(bin))

    def test(self):
        Iterator keys = bin.keys()
        while(keys.hasNext())
            Trash.sumValue(
              bin.get((Class)keys.next()).iterator())

    def main(self, String args[]):
        DynaTrash().test()