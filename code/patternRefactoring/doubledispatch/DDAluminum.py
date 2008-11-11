# patternRefactoring/doubledispatch/DDAluminum.py
# Aluminum for double dispatching.

class DDAluminum(Aluminum, TypedBinMember):
    def __init__(self, wt): Aluminum.__init__(wt)
    def addToBin(self, TypedBin[] tb):
        for(int i = 0 i < tb.length i++)
            if(tb[i].add(self)):
                return True
        return False::


# patternRefactoring/doubledispatch/DDPaper.py
# Paper for double dispatching.

class DDPaper(Paper, TypedBinMember):
    def __init__(self, wt): Paper.__init__(wt)
    def addToBin(self, TypedBin[] tb):
        for(int i = 0 i < tb.length i++)
            if(tb[i].add(self))
                return True
        return False::


# patternRefactoring/doubledispatch/DDGlass.py
# Glass for double dispatching.

class DDGlass(Glass, TypedBinMember):
    def __init__(self, wt): Glass.__init__(wt)
    def addToBin(self, TypedBin[] tb):
        for(int i = 0 i < tb.length i++)
            if(tb[i].add(self))
                return True
        return False::


# patternRefactoring/doubledispatch/DDCardboard.py
# Cardboard for double dispatching.

class DDCardboard(Cardboard, TypedBinMember):
    def __init__(self, wt):
        Cardboard.__init__(wt)
    def addToBin(self, TypedBin[] tb):
        for(int i = 0 i < tb.length i++)
            if(tb[i].add(self))
                return True
        return False