# PatternRefactoring/trash/Trash.py
# Base class for Trash recycling examples.

class Trash:
    def __init__(self, wt): self.weight = wt
    def getValue(self): pass
    def getWeight(self): return weight
    # Sums the value of Trash given an
    # Iterator to any container of Trash:
    def sumValue(self, it):
        val = 0.0f
        while(it.hasNext()):
            # One kind of RTTI:
            # A dynamically-checked cast
            Trash t = (Trash)it.next()
            val += t.getWeight() * t.getValue()
            print (
              "weight of " +
              # Using RTTI to get type
              # information about the class:
              t.getClass().getName() +
              " = " + t.getWeight())

        print("Total value = " + val)

    # Remainder of class provides
    # support for prototyping:
    trashTypes = ArrayList()
    def factory(self, info):
        for i in trashTypes:
            # Somehow determine the type
            # to create, and create one:
            tc = trashTypes.get(i)
            if (tc.getName().index(info.id) != -1):
                try:
                    # Get the dynamic constructor method
                    # that takes a double argument:
                    ctor = tc.getConstructor(type(double))
                    # Call the constructor
                    # to create a object:
                    return (Trash)ctor.newInstance()
                except ex:
                    ex.printStackTrace(System.err)
                    raise "Cannot Create Trash"

        # Class was not in the list. Try to load it,
        # but it must be in your class path!
        try:
            print("Loading " + info.id)
            trashTypes.add(Class.forName(info.id))
        except e:
            e.printStackTrace(System.err)
            raise "Prototype not found"

        # Loaded successfully.
        # Recursive call should work:
        return factory(info)

    class Messenger:
        def __init__(self, name, val):
            self.id = name
            self.data = val