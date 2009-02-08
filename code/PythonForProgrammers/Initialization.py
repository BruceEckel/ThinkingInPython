# QuickPython/Initialization.py
"""
For text:
1) Doesn't automatically call base class constructor except in 1 special case.
2) Doesn't force base-class constructor call to happen first.
3) __new__ is always called
4) __new__ isn't always called first except in default case.

Do the python syntax checkers check for this?
PyChecker, pylint, PyFlakes
"""

def trace(msg, self_dscr, self, *args, **kwargs):
     print (msg + "\n" 
            + self_dscr + ": " + str(self) 
            + ", args: " + str(args) 
            + ", kwargs: " + str(kwargs))

class Foo(object):
     def __new__(cls, *args, **kwargs):
          trace("in Foo new", "cls", cls, *args, **kwargs) 
          return super(Foo, cls).__new__(cls)
     def __init__(self, *args, **kwargs):
          super(Foo, self).__init__()
          trace("in Foo init", "self", self, *args, **kwargs)

print "Creating Foo object:"
f = Foo()

class Bar(Foo):
    def __init__(self, x):
         print "in Bar init"

print "Creating Bar object:"
b = Bar(1) 

class Baz(Foo):
    def __init__(self, x):
         super(Baz, self).__init__(self, x)
         print "in Baz init"

print "Creating Baz object:"
b = Baz(1) 

class DefaultInit(object):
     def __init__(self):
          print "in DefaultInit"

class Derived(DefaultInit): pass

d = Derived()

class Derived2(DefaultInit):
     def __init__(self):
          print "in Derived2 init"

d2 = Derived2()
