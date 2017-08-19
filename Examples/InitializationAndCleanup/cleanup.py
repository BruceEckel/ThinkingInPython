# InitializationAndCleanup/cleanup.py
class Counter:
    Count = 0   # Number of objects of this class
    def __init__(self, name):
        self.name = name
        print name, 'created'
        Counter.Count += 1
    def __del__(self):
        print self.name, 'deleted'
        Counter.Count -= 1
        if Counter.Count == 0:
            print 'Last Counter object deleted'
        else:
            print Counter.Count, 'Counter objects remaining'

x = Counter("First")
del x
