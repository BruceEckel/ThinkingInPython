# Metaclasses/SimpleMeta3.py
# A function for __metaclass__ in Python 2.x

class Simple4(object):
    def __metaclass__(name, bases, nmspc):
        cls = type(name, bases, nmspc)
        cls.uses_metaclass = lambda self : "Yes!"
        return cls

simple = Simple4()
print simple.uses_metaclass()

""" Output:
Yes!
"""