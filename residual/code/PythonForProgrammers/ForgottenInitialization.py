# QuickPython/ForgottenInitialization.py

class Base(object):
     def __init__(self, x):
          self.x = x
     def f(self):
          print(self.x)

class Derived1(Base):
     # Base __init__() is passed through
     pass

Derived1(11).f()

class Derived2(Base):
     def __init__(self, y):
          "Init redefined, but forgot to call base-class init"
          self.y = y
     def f2(self):
          print(self.y)

d = Derived2(22)
d.f2()
try:
     d.f()
except:
     print "call to f() failed"

class Derived3(Base):
     def __init__(self, y):
          "Base-class call remembered"
          super(Derived3, self).__init__(y)

d = Derived3(33)
d.f()
