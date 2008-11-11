# patternRefactoring/clip3.py
    def factory(messenger):
        switch(messenger.type):
            default: # To quiet the compiler
            case 0:
                return Aluminum(messenger.data)
            case 1:
                return Paper(messenger.data)
            case 2:
                return Glass(messenger.data)
            # Two lines here:
            case 3:
                return Cardboard(messenger.data)